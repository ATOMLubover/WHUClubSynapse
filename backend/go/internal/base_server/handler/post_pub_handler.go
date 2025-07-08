package handler

import (
	"log/slog"
	"whuclubsynapse-server/internal/base_server/service"
	"whuclubsynapse-server/internal/shared/dbstruct"

	"github.com/kataras/iris/v12"
	"github.com/kataras/iris/v12/mvc"
)

type PostPubHandler struct {
	PostService service.PostService
	Logger      *slog.Logger
}

func (h *PostPubHandler) BeforeActivation(b mvc.BeforeActivation) {
	//b.Handle("PUT", "/proc_create", "PutProcAppliForCreatePost")

	b.Handle("PUT", "/ban/{id:int}", "PutBanPost")
	b.Handle("PUT", "/pin/{id:int}", "PutPinPost")
}

func (h *PostPubHandler) PutBanPost(ctx iris.Context, id int) {
	userRole := ctx.Values().GetString("user_claims_user_role")
	if userRole != dbstruct.ROLE_PUBLISHER &&
		userRole != dbstruct.ROLE_ADMIN {
		ctx.StatusCode(iris.StatusForbidden)
		return
	}

	err := h.PostService.BanPost(userRole, id)
	if err != nil {
		h.Logger.Error("封禁帖子失败",
			"error", err, "post_id", id,
		)

		ctx.StatusCode(iris.StatusBadRequest)
		ctx.Text("无法封禁指定帖子")
		return
	}

	ctx.Text("封禁帖子成功")
}

func (h *PostPubHandler) PutPinPost(ctx iris.Context, id int) {
	err := h.PostService.PinPost(id)
	if err != nil {
		h.Logger.Error("置顶帖子失败",
			"error", err, "post_id", id,
		)

		ctx.StatusCode(iris.StatusBadRequest)
		ctx.Text("无法置顶指定帖子")
		return
	}

	ctx.Text("置顶帖子成功")
}

// func (h *PostPubHandler) PutProcAppliForCreatePost(ctx iris.Context) {
// 	var reqBody dto.ProcCreatePostRequest
// 	if err := ctx.ReadJSON(&reqBody); err != nil {
// 		h.Logger.Info("ProcCreatePost请求格式错误", "error", err)

// 		ctx.StatusCode(iris.StatusBadRequest)
// 		ctx.Text("请求格式错误")
// 		return
// 	}

// 	switch reqBody.Result {
// 	case "approve":
// 		oriAppli, curPost, err := h.PostService.
// 			ApproveAppliForCreatePost(reqBody.CreatePostAppliId)
// 		if err != nil {
// 			h.Logger.Info("通过帖子创建申请失败",
// 				"error", err, "appli_id", reqBody.CreatePostAppliId,
// 			)

// 			ctx.StatusCode(iris.StatusInternalServerError)
// 			ctx.Text("通过帖子创建申请失败")
// 			return
// 		}

// 		if err := h.PostService.TransferPost(oriAppli, curPost); err != nil {
// 			h.Logger.Info("转移临时帖子失败",
// 				"error", err, "draft_url", oriAppli.DraftContentUrl,
// 			)

// 			ctx.StatusCode(iris.StatusInternalServerError)
// 			ctx.Text("帖子通过失败，无法转移")
// 			return
// 		}

// 		ctx.Text("通过帖子创建申请成功")
// 		return

// 	case "reject":
// 		if err := h.PostService.RejectAppliForCreatePost(reqBody.CreatePostAppliId, reqBody.Reason); err != nil {
// 			h.Logger.Info("拒绝帖子创建申请失败",
// 				"error", err, "appli_id", reqBody.CreatePostAppliId,
// 			)

// 			ctx.StatusCode(iris.StatusInternalServerError)
// 			ctx.Text("拒绝帖子创建申请失败")
// 			return
// 		}

// 	default:
// 		ctx.StatusCode(iris.StatusBadRequest)
// 		ctx.Text("result参数错误")
// 		return
// 	}
// }
