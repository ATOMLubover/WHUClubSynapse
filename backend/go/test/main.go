package main

import (
	"fmt"
	"log"
	"net/http"
	"time"
)

func sseHandler(w http.ResponseWriter, r *http.Request) {
	// 设置 SSE 必要的响应头
	w.Header().Set("Content-Type", "text/event-stream")
	w.Header().Set("Cache-Control", "no-cache")
	w.Header().Set("Connection", "keep-alive")

	// 获取 FlushWriter 接口，用于立即将数据发送给客户端
	flusher, ok := w.(http.Flusher)
	if !ok {
		http.Error(w, "Streaming unsupported!", http.StatusInternalServerError)
		return
	}

	log.Println("Client connected for SSE at /test")

	// 循环发送多个事件
	for i := 0; i < 10; i++ { // 我们发送10条消息
		message := fmt.Sprintf("data: 这是第 %d 条消息，时间是 %s\n\n", i+1, time.Now().Format("15:04:05.000"))
		fmt.Fprint(w, message)

		// 立即刷新缓冲区，确保数据发送到客户端
		flusher.Flush()

		// 等待 100 毫秒
		time.Sleep(100 * time.Millisecond)
	}

	log.Println("Finished sending SSE messages and closing connection for /test")
	// 注意：当处理函数返回时，连接会自动关闭。
}

func main() {
	http.HandleFunc("/test", sseHandler)

	fmt.Println("Server listening on :8085")
	fmt.Println("Visit http://localhost:8080/test to see the SSE response with multiple messages.")
	log.Fatal(http.ListenAndServe(":8085", nil))
}
