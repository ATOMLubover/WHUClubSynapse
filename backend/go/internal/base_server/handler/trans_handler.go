package handler

import (
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

	b.Handle("POST", "/llm/{route:string}", "PostTransLlm")
	b.Handle("POST", "/rag/{route:string}", "PostTransRag")
}

func (h *TransHandler) GetTransLlm(ctx iris.Context, route string) {
	req := ctx.Request().Clone(ctx.Request().Context())

	req.URL, _ = url.Parse(h.LlmAddr + "/" + route)
	req.RequestURI = ""

	req.Host = strings.TrimPrefix(h.LlmAddr, "https://")
	req.Header.Set("Host", req.Host)

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

	ctx.StatusCode(res.StatusCode)

	for {
		_, err := io.Copy(ctx.ResponseWriter(), res.Body)
		if err != nil {
			if err != io.EOF {
				h.Logger.Error("SSE转发中错误", "error", err)
			}
			break
		}
		ctx.ResponseWriter().Flush()
	}

	h.Logger.Debug("SSE 转发结束")
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

	ctx.StatusCode(res.StatusCode)

	for {
		_, err := io.Copy(ctx.ResponseWriter(), res.Body)
		if err != nil {
			if err != io.EOF {
				h.Logger.Error("SSE转发中错误", "error", err)
			}
			break
		}
		ctx.ResponseWriter().Flush()
	}

	h.Logger.Debug("SSE 转发结束")
}
