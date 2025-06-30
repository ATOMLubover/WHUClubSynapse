package handler

import (
	"github.com/gorilla/websocket"
	"github.com/kataras/iris/v12"
)

type IrisMiddleware func(iris.Context)

var httpInterceptor IrisMiddleware = func(ctx iris.Context) {
	if websocket.IsWebSocketUpgrade(ctx.Request()) {
		ctx.StopWithText(iris.StatusBadRequest,
			"该接口只支持HTTP请求")
		return
	}

	ctx.Next()
}

var websockInterceptor IrisMiddleware = func(ctx iris.Context) {
	if !websocket.IsWebSocketUpgrade(ctx.Request()) {
		ctx.StopWithText(iris.StatusBadRequest,
			"该接口只支持WebSocket请求")
		return
	}

	ctx.Next()
}
