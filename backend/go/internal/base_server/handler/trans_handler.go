package handler

import (
	"bufio"
	"bytes"
	"io"
	"log/slog"
	"net/http"
	"net/url"
	"strings"
	"whuclubsynapse-server/internal/base_server/baseconfig"

	"github.com/kataras/iris/v12"
	"github.com/kataras/iris/v12/mvc"
)

func InitTransHandler(parent *mvc.Application, cfg *baseconfig.Config) {
	transApp := parent.Party("/trans")

	handler := &TransHandler{
		LlmAddr: cfg.LlmAddr,
		RagAddr: cfg.RagAddr,
	}

	transApp.Handle(handler)
}

type TransHandler struct {
	LlmAddr string
	RagAddr string

	Logger *slog.Logger
}

func (h *TransHandler) BeforeActivation(b mvc.BeforeActivation) {
	b.Handle("GET", "/llm/{route:string}", "GetTransLlm")
	b.Handle("GET", "/rag/{route:string}", "GetTransRag")

	b.Handle("POST", "/llm/{route:string}", "PostTransLlm")
	b.Handle("POST", "/rag/{route:string}", "PostTransRag")
}

func (h *TransHandler) GetTransLlm(ctx iris.Context, route string) {
	req := ctx.Request().Clone(ctx.Request().Context())

	req.URL, _ = url.Parse(h.LlmAddr + "/" + route)
	req.RequestURI = ""

	req.Host = strings.TrimPrefix(h.LlmAddr, "https://")
	req.Header.Set("Host", req.Host)

	h.Logger.Info("LLM请求", "url", req.URL.String())

	res, err := http.DefaultClient.Do(req)
	if err != nil {
		h.Logger.Error("LLM服务器请求失败", "error", err)

		ctx.StatusCode(iris.StatusServiceUnavailable)
		ctx.Text("LLM服务器暂不可用")
		return
	}
	defer res.Body.Close()

	for key, values := range res.Header {
		for _, value := range values {
			ctx.ResponseWriter().Header().Add(key, value)
		}
	}
	// 在处理完请求后，强制重新设置 CORS 头部
	ctx.ResponseWriter().Header().Set("Access-Control-Allow-Origin", "*")
	ctx.ResponseWriter().Header().Set("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS")
	ctx.ResponseWriter().Header().Set("Access-Control-Allow-Headers", "*")
	ctx.ResponseWriter().Header().Set("Access-Control-Max-Age", "86400")

	ctx.StatusCode(res.StatusCode)
	io.Copy(ctx.ResponseWriter(), res.Body)
}

func (h *TransHandler) PostTransLlm(ctx iris.Context, route string) {
	bodyBytes, err := io.ReadAll(ctx.Request().Body)
	if err != nil {
		h.Logger.Error("读取原始请求体失败", "error", err)

		ctx.StatusCode(iris.StatusInternalServerError)
		ctx.Text("内部错误：读取请求体失败")
		return
	}

	targetURL := h.LlmAddr + "/" + route
	parsedURL, err := url.Parse(targetURL)
	if err != nil {
		h.Logger.Error("解析LLM目标URL失败", "error", err)

		ctx.StatusCode(iris.StatusInternalServerError)
		ctx.Text("内部错误：LLM目标URL解析失败")
		return
	}

	req, err := http.NewRequest(ctx.Request().Method, parsedURL.String(), io.NopCloser(bytes.NewBuffer(bodyBytes)))
	if err != nil {
		h.Logger.Error("创建LLM请求失败", "error", err)

		ctx.StatusCode(iris.StatusInternalServerError)
		ctx.Text("内部错误：创建LLM请求失败")
		return
	}

	req.RequestURI = ""

	req.Host = strings.TrimPrefix(h.LlmAddr, "https://")
	req.Header.Set("Host", req.Host)

	for key, values := range ctx.Request().Header {
		if strings.EqualFold(key, "Host") || strings.EqualFold(key, "Connection") || strings.EqualFold(key, "Content-Length") {
			continue
		}
		for _, value := range values {
			req.Header.Add(key, value)
		}
	}

	h.Logger.Info("LLM请求", "url", req.URL.String())

	res, err := http.DefaultClient.Do(req)
	if err != nil {
		h.Logger.Error("无法访问LLM服务器", "error", err)

		ctx.StatusCode(iris.StatusServiceUnavailable)
		ctx.Text("LLM服务器暂不可用")
		return
	}
	defer res.Body.Close()

	for key, values := range res.Header {
		for _, value := range values {
			ctx.ResponseWriter().Header().Add(key, value)
		}
	}
	// 在处理完请求后，强制重新设置 CORS 头部
	ctx.ResponseWriter().Header().Set("Access-Control-Allow-Origin", "*")
	ctx.ResponseWriter().Header().Set("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS")
	ctx.ResponseWriter().Header().Set("Access-Control-Allow-Headers", "*")
	ctx.ResponseWriter().Header().Set("Access-Control-Max-Age", "86400")

	ctx.StatusCode(res.StatusCode)

	if !strings.Contains(strings.ToLower(res.Header.Get("Content-Type")), "text/event-stream") {
		h.Logger.Warn("上游响应Content-Type不是text/event-stream，进行普通拷贝", "content-type", res.Header.Get("Content-Type"))
		_, copyErr := io.Copy(ctx.ResponseWriter(), res.Body)
		if copyErr != nil {
			h.Logger.Error("普通转发中错误", "error", copyErr)
		}
		ctx.ResponseWriter().Flush()
		h.Logger.Debug("普通转发结束")
		return
	}

	// 尝试获取 Flusher 接口
	flusher, ok := ctx.ResponseWriter().(http.Flusher)
	if !ok {
		h.Logger.Error("ResponseWriter不支持Flush，无法进行SSE转发")
		http.Error(ctx.ResponseWriter(), "Streaming unsupported!", http.StatusInternalServerError)
		return
	}

	scanner := bufio.NewScanner(res.Body)
	for scanner.Scan() {
		line := scanner.Bytes()
		// 将读取到的行直接写入到下游客户端，并添加换行符以保持SSE格式
		if _, writeErr := ctx.ResponseWriter().Write(append(line, '\n')); writeErr != nil {
			h.Logger.Error("SSE转发写入下游客户端错误", "error", writeErr)
			// 如果写入下游客户端失败，通常表示客户端断开，此时应退出循环
			break
		}
		flusher.Flush() // 每次写入一行后立即刷新，确保数据实时发送
	}

	// 检查Scanner是否在读取过程中遇到了错误（除了io.EOF）
	if err := scanner.Err(); err != nil {
		h.Logger.Error("从上游SSE读取数据时发生错误", "error", err)
	} else {
		// 如果没有错误，且循环结束，意味着上游SSE流已优雅关闭或数据已传输完毕
		h.Logger.Debug("上游SSE流已优雅结束或数据传输完毕")
	}
	h.Logger.Debug("SSE 转发结束")
}

func (h *TransHandler) GetTransRag(ctx iris.Context, route string) {
	req := ctx.Request().Clone(ctx.Request().Context())

	req.URL, _ = url.Parse(h.RagAddr + "/" + route)
	req.RequestURI = ""

	req.Host = strings.TrimPrefix(h.RagAddr, "http://")
	req.Header.Set("Host", req.Host)
	req.Header.Set("Authorization", "super_plus_api_key")

	h.Logger.Info("RAG请求", "url", req.URL.String())

	res, err := http.DefaultClient.Do(req)
	if err != nil {
		h.Logger.Error("RAG服务器请求失败", "error", err)

		ctx.StatusCode(iris.StatusServiceUnavailable)
		ctx.Text("RAG服务器暂不可用")
		return
	}
	defer res.Body.Close()

	for key, values := range res.Header {
		for _, value := range values {
			ctx.ResponseWriter().Header().Add(key, value)
		}
	}
	// 在处理完请求后，强制重新设置 CORS 头部
	ctx.ResponseWriter().Header().Set("Access-Control-Allow-Origin", "*")
	ctx.ResponseWriter().Header().Set("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS")
	ctx.ResponseWriter().Header().Set("Access-Control-Allow-Headers", "*")
	ctx.ResponseWriter().Header().Set("Access-Control-Max-Age", "86400")

	ctx.StatusCode(res.StatusCode)
	io.Copy(ctx.ResponseWriter(), res.Body)
}

func (h *TransHandler) PostTransRag(ctx iris.Context, route string) {
	bodyBytes, err := io.ReadAll(ctx.Request().Body)
	if err != nil {
		h.Logger.Error("读取原始请求体失败", "error", err)

		ctx.StatusCode(iris.StatusInternalServerError)
		ctx.Text("内部错误：读取请求体失败")
		return
	}

	targetURL := h.RagAddr + "/" + route
	parsedURL, err := url.Parse(targetURL)
	if err != nil {
		h.Logger.Error("解析RAG目标URL失败", "error", err)

		ctx.StatusCode(iris.StatusInternalServerError)
		ctx.Text("内部错误：RAG目标URL解析失败")
		return
	}

	req, err := http.NewRequest(ctx.Request().Method, parsedURL.String(), io.NopCloser(bytes.NewBuffer(bodyBytes)))
	if err != nil {
		h.Logger.Error("创建RAG请求失败", "error", err)

		ctx.StatusCode(iris.StatusInternalServerError)
		ctx.Text("内部错误：创建RAG请求失败")
		return
	}

	req.RequestURI = ""

	req.Host = strings.TrimPrefix(h.RagAddr, "http://")
	req.Header.Set("Host", req.Host)
	req.Header.Set("Authorization", "super_plus_api_key")

	for key, values := range ctx.Request().Header {
		if strings.EqualFold(key, "Host") || strings.EqualFold(key, "Connection") || strings.EqualFold(key, "Content-Length") {
			continue
		}
		for _, value := range values {
			req.Header.Add(key, value)
		}
	}

	h.Logger.Info("RAG请求", "url", req.URL.String())

	res, err := http.DefaultClient.Do(req)
	if err != nil {
		h.Logger.Error("无法访问RAG服务器", "error", err)

		ctx.StatusCode(iris.StatusServiceUnavailable)
		ctx.Text("RAG服务器暂不可用")
		return
	}
	defer res.Body.Close()

	for key, values := range res.Header {
		for _, value := range values {
			ctx.ResponseWriter().Header().Add(key, value)
		}
	}
	ctx.ResponseWriter().Header().Set("Access-Control-Allow-Origin", "*")
	ctx.ResponseWriter().Header().Set("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS")
	ctx.ResponseWriter().Header().Set("Access-Control-Allow-Headers", "*")
	ctx.ResponseWriter().Header().Set("Access-Control-Max-Age", "86400")

	ctx.StatusCode(res.StatusCode)

	if !strings.Contains(strings.ToLower(res.Header.Get("Content-Type")), "text/event-stream") {
		h.Logger.Warn("上游响应Content-Type不是text/event-stream，进行普通拷贝", "content-type", res.Header.Get("Content-Type"))
		_, copyErr := io.Copy(ctx.ResponseWriter(), res.Body)
		if copyErr != nil {
			h.Logger.Error("普通转发中错误", "error", copyErr)
		}
		ctx.ResponseWriter().Flush()
		h.Logger.Debug("普通转发结束")
		return
	}

	// 尝试获取 Flusher 接口
	flusher, ok := ctx.ResponseWriter().(http.Flusher)
	if !ok {
		h.Logger.Error("ResponseWriter不支持Flush，无法进行SSE转发")
		http.Error(ctx.ResponseWriter(), "Streaming unsupported!", http.StatusInternalServerError)
		return
	}

	scanner := bufio.NewScanner(res.Body)
	for scanner.Scan() {
		line := scanner.Bytes()
		// 将读取到的行直接写入到下游客户端，并添加换行符以保持SSE格式
		if _, writeErr := ctx.ResponseWriter().Write(append(line, '\n')); writeErr != nil {
			h.Logger.Error("SSE转发写入下游客户端错误", "error", writeErr)
			// 如果写入下游客户端失败，通常表示客户端断开，此时应退出循环
			break
		}
		flusher.Flush() // 每次写入一行后立即刷新，确保数据实时发送
	}

	// 检查Scanner是否在读取过程中遇到了错误（除了io.EOF）
	if err := scanner.Err(); err != nil {
		h.Logger.Error("从上游SSE读取数据时发生错误", "error", err)
	} else {
		// 如果没有错误，且循环结束，意味着上游SSE流已优雅关闭或数据已传输完毕
		h.Logger.Debug("上游SSE流已优雅结束或数据传输完毕")
	}

	h.Logger.Debug("SSE 转发结束")
}
