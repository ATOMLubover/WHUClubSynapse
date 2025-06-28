package handler

import (
	"log/slog"
	"whuclubsynapse-server/internal/base_server/dto"
	"whuclubsynapse-server/internal/base_server/model"
	"whuclubsynapse-server/internal/base_server/service"
	"whuclubsynapse-server/internal/shared/jwtutil"

	"github.com/kataras/iris/v12"
	"github.com/kataras/iris/v12/mvc"
)

type ClubAdminHandler struct {
	JwtFactory *jwtutil.CliamsFactory[model.UserClaims]

	ClubService service.ClubService

	Logger *slog.Logger
}

func (h *ClubAdminHandler) BeforeActivation(b mvc.BeforeActivation) {
	b.Handle("PUT", "/proc_create", "PutProcAppliForCreateClub")
	b.Handle("PUT", "/proc_update", "PutProcAppliForUpdateClub")
}

func (h *ClubAdminHandler) PutProcAppliForCreateClub(ctx iris.Context) {
	var reqBody dto.ProcCreateClubRequest
	if err := ctx.ReadJSON(&reqBody); err != nil {
		h.Logger.Info("ProcCreateClub请求格式错误", "error", err)

		ctx.StatusCode(iris.StatusBadRequest)
		ctx.Text("请求格式错误")
		return
	}

	switch reqBody.Result {
	case "approve":
		if err := h.ClubService.ApproveAppliForCreateClub(reqBody.CreateClubAppliId); err != nil {
			h.Logger.Info("通过社团创建申请失败",
				"error", err, "appli_id", reqBody.CreateClubAppliId,
			)

			ctx.StatusCode(iris.StatusInternalServerError)
			ctx.Text("通过社团创建申请失败")
			return
		}

	case "reject":
		if err := h.ClubService.RejectAppliForCreateClub(reqBody.CreateClubAppliId, reqBody.Reason); err != nil {
			h.Logger.Info("拒绝社团创建申请失败",
				"error", err, "appli_id", reqBody.CreateClubAppliId,
			)

			ctx.StatusCode(iris.StatusInternalServerError)
			ctx.Text("拒绝社团创建申请失败")
			return
		}

	default:
		ctx.StatusCode(iris.StatusBadRequest)
		ctx.Text("result参数错误")
		return
	}

	ctx.Text("处理申请成功")
}

func (h *ClubAdminHandler) PutProcAppliForUpdateClub(ctx iris.Context) {
	var reqBody dto.ProcUpdateClubRequest
	if err := ctx.ReadJSON(&reqBody); err != nil {
		h.Logger.Info("ProcCreateClub请求格式错误", "error", err)

		ctx.StatusCode(iris.StatusBadRequest)
		ctx.Text("请求格式错误")
		return
	}

	switch reqBody.Result {
	case "approve":
		if err := h.ClubService.ApproveAppliForCreateClub(reqBody.UpdateAppliId); err != nil {
			h.Logger.Info("通过社团更新申请失败",
				"error", err, "appli_id", reqBody.UpdateAppliId,
			)

			ctx.StatusCode(iris.StatusInternalServerError)
			ctx.Text("通过社团更新申请失败")
			return
		}

	case "reject":
		if err := h.ClubService.RejectAppliForCreateClub(reqBody.UpdateAppliId, reqBody.Reason); err != nil {
			h.Logger.Info("拒绝社团更新申请失败",
				"error", err, "appli_id", reqBody.UpdateAppliId,
			)

			ctx.StatusCode(iris.StatusInternalServerError)
			ctx.Text("拒绝社团更新申请失败")
			return
		}

	default:
		ctx.StatusCode(iris.StatusBadRequest)
		ctx.Text("result参数错误")
		return
	}

	ctx.Text("通过社团更新申请成功")
}
