---
title: 网络编程
description: ""
pubDate: "2025-2-10"
categories:
    - tech
tags:
    - csapp
---

# C/S模型
![](attachments/Pasted%20image%2020250210161823.png)

![](attachments/Pasted%20image%2020250210162123.png)

# 计算机网络
简单讲了计算机网络的知识,这我可不陌生😋.

# 套接字
对应用来说,套接字是交流的端点;对内核来说,套接字是一个文件描述符供应用从网络读写.
![](attachments/Pasted%20image%2020250210190312.png)
> *不得不说,外国教学的图片都好好看喔*

> 这部分套接字操作的介绍,可见于我的OneNote笔记本.

将socket和它使用的协议/IP地址等信息联系起来,就抽象成了一个结构体:
```c
struct sockaddr { 
	uint16_t sa_family; /* Protocol family */ 
	char sa_data[14]; /* Address data. */ 
};
```
在实际应用中,使用更具体的
```c
struct sockaddr_in { 
	uint16_t sin_family; /* Protocol family (always AF_INET) */ 
	uint16_t sin_port; /* Port num in network byte order */ 
	struct in_addr sin_addr; /* IP addr in network byte order */ 
	unsigned char sin_zero[8]; /* Pad to sizeof(struct sockaddr) */ 
};
```
![](attachments/Pasted%20image%2020250210191248.png)


一个简单的串行C/S交互图:
![](attachments/Pasted%20image%2020250210210410.png)

1. 创建socket文件描述符
	```c
	int socket(int domain, int type, int protocol);
	```
2. 绑定socket
	```c
	int bind(int sockfd, struct sockaddr *addr, socklen_t addrlen);
	```
3. 监听socket
	```c
	int listen(int sockfd, int backlog);
	```
4. 接收请求,返回另一个用于I/O的socket
	```c
	int accept(int listenfd, struct sockaddr *addr, int *addrlen);
	```
5. 请求连接
	```c
	int connect(int clientfd, struct sockaddr *addr, socklen_t addrlen);
	```
	![](attachments/Pasted%20image%2020250210234746.png)

最佳实践,是利用`getaddrinfo`函数返回的信息.

6. `getaddrinfo`函数:查询处理主机名,主机地址,端口,协议等信息.
	优点:同时适用于IPv4和IPv6;可重入(能安全用于多线程程序)
	```c
	int getaddrinfo(const char *host, /* Hostname or address */ 
					const char *service, /* Port or service name */ 
					const struct addrinfo *hints,/* Input parameters */ 
					struct addrinfo **result); /* Output linked list */ 
					
	void freeaddrinfo(struct addrinfo *result); /* Free linked list */ 
	const char *gai_strerror(int errcode); /* Return error msg */
	```
	`getaddrinfo`函数返回的结果是一个链表:
	![](attachments/Pasted%20image%2020250210213057.png)
	包含主机的规范名,IP地址等信息.
	对于客户端,遍历这个链表直到socket调用`connect`成功;
	对于服务端,遍历这个链表直到socket调用`bind`成功.
	链表的每个节点是一个`addinfo struct`结构体:
	```c
	struct addrinfo { 
		int ai_flags; /* Hints argument flags */ 
		int ai_family; /* First arg to socket function */ 
		int ai_socktype; /* Second arg to socket function */ 
		int ai_protocol; /* Third arg to socket function */ 
		char *ai_canonname; /* Canonical host name */ 
		size_t ai_addrlen; /* Size of ai_addr struct */ 
		struct sockaddr *ai_addr; /* Ptr to socket address structure */ 
		struct addrinfo *ai_next; /* Ptr to next item in linked list */ 
	};
	```
	- 用例
	1. 客户端获取服务器可连接的IP地址
		```c
		int open_clientfd(char *hostname, char *port) { 
			int clientfd; 
			struct addrinfo hints, *listp, *p; /* Get a list of potential server addresses */ 
			memset(&hints, 0, sizeof(struct addrinfo)); 
			hints.ai_socktype = SOCK_STREAM; /* Open a connection */ 
			hints.ai_flags = AI_NUMERICSERV; /* …using numeric port arg. */ 
			hints.ai_flags |= AI_ADDRCONFIG; /* Recommended for connections */ 
			Getaddrinfo(hostname, port, &hints, &listp);
			/* Walk the list for one that we can successfully connect to */ 
			for (p = listp; p; p = p->ai_next) { 
				/* Create a socket descriptor */ 
				if ((clientfd = socket(p->ai_family, p->ai_socktype, p->ai_protocol)) < 0) 
					continue; /* Socket failed, try the next */ 
					
				/* Connect to the server */ 
				if (connect(clientfd, p->ai_addr, p->ai_addrlen) != -1) 
					break; /* Success */ 
				Close(clientfd); /* Connect failed, try another */ 
			} 
			
			/* Clean up */ 
			Freeaddrinfo(listp); 
			if (!p) /* All connects failed */ 
				return -1; 
			else /* The last connect succeeded */ 
				return clientfd; 
		}
		```
		2. 服务器创建监听套接字
			```c
			int open_listenfd(char *port) { 
				struct addrinfo hints, *listp, *p; 
				int listenfd, optval=1; /* Get a list of potential server addresses */ 
				memset(&hints, 0, sizeof(struct addrinfo)); 
				hints.ai_socktype = SOCK_STREAM; /* Accept connect. */ 
				hints.ai_flags = AI_PASSIVE | AI_ADDRCONFIG; /* …on any IP addr */ 
				hints.ai_flags |= AI_NUMERICSERV; /* …using port no. */ 
				Getaddrinfo(NULL, port, &hints, &listp);
				
				/* Walk the list for one that we can bind to */ 
				for (p = listp; p; p = p->ai_next) { 
					/* Create a socket descriptor */ 
					if ((listenfd = socket(p->ai_family, p->ai_socktype, p->ai_protocol)) < 0) 
						continue; /* Socket failed, try the next */ 
					
					/* Eliminates "Address already in use" error from bind */ 
					Setsockopt(listenfd, SOL_SOCKET, SO_REUSEADDR, (const void *)&optval , sizeof(int)); 
					
					/* Bind the descriptor to the address */ 
					if (bind(listenfd, p->ai_addr, p->ai_addrlen) == 0) 
						break; /* Success */ 
					Close(listenfd); /* Bind failed, try the next */ 
				}
				/* Clean up */ 
				Freeaddrinfo(listp); 
				if (!p) /* No address worked */ 
					return -1; 
					
				/* Make it a listening socket ready to accept conn. requests */ 
				if (listen(listenfd, LISTENQ) < 0) { 
					Close(listenfd); 
					return -1; 
				} 
				return listenfd; 
			}
			```
			

> `getnameinfo`函数:根据IP地址查询域名
> ```c
> int getnameinfo(const struct sockaddr *sa, 
> 				socklen_t salen, /* In: socket addr */ 
> 				char *host, size_t hostlen, /* Out: host */ 
> 				char *serv, size_t servlen, /* Out: service */ 
> 				int flags);                 /* optional flags */
> ```
> 与`getaddrinfo`类似.

# Web服务器
服务器和客户端交流使用的应用层协议是超文本传输协议(HTTP).当前是版本HTTP/1.1
- 动态和静态内容
	静态内容:HTML,图片
	动态内容:根据客户端的行为,有服务器执行程序产生.

- HTTP请求
	```
	<method> <uri> <version>
	```
	`<method>`可以是GET,POST,OPTIONS,HEAD,PUT,DELETE,TRACE
	`<uri>`是统一资源标识符
	`<version>`是HTTP版本(HTTP/1.0或HTTP/1.1)
## Tiny服务器
Tiny服务器是本课程提供的一个Web服务器示例,只有200多行C语言代码.可以请求静态和动态内容.
请求方式是:
`GET <URI> <version>`
动态内容在`/cgi-bin/`下
	![](attachments/Pasted%20image%2020250211110110.png)
   ![](attachments/Pasted%20image%2020250211110132.png)

这个子进程通过通用网关接口(CGI:Common Gateway Interface)实现.
目前, cgi-bin里面有一个程序adder,通过设置URI为
/cgi-bin/adder?15213&18213
将参数传给程序.
变量从"?"起始,用"&"分隔.如果用空格,用"+"或"%20".
CGI程序直接将输出重定向到客户端的套接字.

