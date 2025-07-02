package handler

import (
	"log/slog"
	"whuclubsynapse-server/internal/base_server/dto"
	"whuclubsynapse-server/internal/base_server/model"
	"whuclubsynapse-server/internal/base_server/service"
	"whuclubsynapse-server/internal/shared/dbstruct"
	"whuclubsynapse-server/internal/shared/jwtutil"

	"github.com/kataras/iris/v12"
	"github.com/kataras/iris/v12/mvc"
)

type ClubPubHandler struct {
	JwtFactory *jwtutil.CliamsFactory[model.UserClaims]

	ClubService service.ClubService

	Logger *slog.Logger
}

func (h *ClubPubHandler) BeforeActivation(b mvc.BeforeActivation) {
	b.Handle("GET", "/join_applis/{id:int}", "GetJoinApplisForClub")

	b.Handle("POST", "/update", "PostApplyForUpdateClubInfo")

	b.Handle("PUT", "/proc_join", "PutProcAppliForJoinClub")
}

func (h *ClubPubHandler) PostApplyForUpdateClubInfo(ctx iris.Context, id int) {
	var reqBody dto.UpdateClubInfoRequest
	if err := ctx.ReadJSON(&reqBody); err != nil {
		h.Logger.Error("请求格式错误", "error", err)

		ctx.StatusCode(iris.StatusBadRequest)
		ctx.Text("请求格式错误")
		return
	}

	err := h.ClubService.ApplyForUpdateClub(
		dbstruct.Club{
			ClubId:      uint(id),
			Name:        reqBody.Name,
			Description: reqBody.Desc,
		})
	if err != nil {
		h.Logger.Error("申请更新社团信息失败",
			"error", err, "club_id", id,
		)

		ctx.StatusCode(iris.StatusBadRequest)
		ctx.Text("无法申请更新社团信息")
		return
	}

	ctx.Text("更新社团信息申请成功")
}

func (h *ClubPubHandler) PutProcAppliForJoinClub(ctx iris.Context) {
	var reqBody dto.ProcJoinClubRequest
	if err := ctx.ReadJSON(&reqBody); err != nil {
		h.Logger.Info("ProcCreateClub请求格式错误", "error", err)

		ctx.StatusCode(iris.StatusBadRequest)
		ctx.Text("请求格式错误")
		return
	}

	switch reqBody.Result {
	case "approve":
		if err := h.ClubService.ApproveAppliForJoinClub(reqBody.JoinAppliId); err != nil {
			h.Logger.Info("通过社团加入申请失败",
				"error", err, "appli_id", reqBody.JoinAppliId,
			)

			ctx.StatusCode(iris.StatusInternalServerError)
			ctx.Text("通过社团加入申请失败")
			return
		}

	case "reject":
		if err := h.ClubService.RejectAppliForJoinClub(reqBody.JoinAppliId, reqBody.Reason); err != nil {
			h.Logger.Info("拒绝社团加入申请失败",
				"error", err, "appli_id", reqBody.JoinAppliId,
			)

			ctx.StatusCode(iris.StatusInternalServerError)
			ctx.Text("拒绝社团加入申请失败")
			return
		}

	default:
		ctx.StatusCode(iris.StatusBadRequest)
		ctx.Text("result参数错误")
		return
	}

	ctx.Text("通过社团更新申请成功")
}

func (h *ClubPubHandler) GetJoinApplisForClub(ctx iris.Context, id int) {
	joinApplis, err := h.ClubService.
		GetJoinApplisForClub(id)
	if err != nil {
		h.Logger.Error("获取社团加入申请列表失败", "error", err)

		ctx.StatusCode(iris.StatusBadRequest)
		ctx.Text("无法获取社团加入申请列表")
		return
	}

	var resApplisList []*dto.JoinClubAppliResponse
	for _, appli := range joinApplis {
		resApplisList = append(resApplisList, &dto.JoinClubAppliResponse{
			AppliId:      int(appli.JoinAppliId),
			AppliedAt:    appli.AppliedAt.Format("2006-01-02 15:04:05"),
			ClubId:       int(appli.ClubId),
			ApplicantId:  int(appli.UserId),
			Reason:       appli.ApplyReason,
			Status:       appli.Status,
			RejectReason: appli.RejectedReason,
			ReviewedAt:   appli.RejectedReason,
		})
	}

	ctx.JSON(resApplisList)
}
