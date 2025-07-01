package handler

import (
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
	req := ctx.Request().Clone(ctx.Request().Context())
	req.URL, _ = url.Parse(h.LlmAddr + route)

	res, err := http.DefaultClient.Do(req)
	if err != nil {
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

func (h *TransHandler) PostTransRag(ctx iris.Context, route string) {
	req := ctx.Request().Clone(ctx.Request().Context())
	req.URL, _ = url.Parse(h.LlmAddr + route)

	res, err := http.DefaultClient.Do(req)
	if err != nil {
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
