package handler

import (
	"log/slog"
	"whuclubsynapse-server/internal/base_server/dto"
	"whuclubsynapse-server/internal/base_server/model"
	"whuclubsynapse-server/internal/base_server/redisimpl"
	"whuclubsynapse-server/internal/base_server/service"
	"whuclubsynapse-server/internal/shared/jwtutil"

	"github.com/kataras/iris/v12"
	"github.com/kataras/iris/v12/mvc"
)

type ClubAdminHandler struct {
	JwtFactory *jwtutil.CliamsFactory[model.UserClaims]

	ClubService  service.ClubService
	RedisService redisimpl.RedisClientService

	Logger *slog.Logger
}

func (h *ClubAdminHandler) BeforeActivation(b mvc.BeforeActivation) {
	b.Handle("PUT", "/proc_create", "PutProcAppliForCreateClub")
	b.Handle("PUT", "/proc_update", "PutProcAppliForUpdateClub")

	b.Handle("GET", "/create_list", "GetCreateList")
	b.Handle("GET", "/update_list", "GetUpdateList")
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
		newClubId, err := h.ClubService.ApproveAppliForCreateClub(
			reqBody.CreateClubAppliId)
		if err != nil {
			h.Logger.Info("通过社团创建申请失败",
				"error", err, "appli_id", reqBody.CreateClubAppliId,
			)

			ctx.StatusCode(iris.StatusInternalServerError)
			ctx.Text("通过社团创建申请失败")
			return
		}

		newClub, err := h.ClubService.GetClubInfo(int(newClubId))
		if err != nil {
			h.Logger.Info("获取新创建的社团信息失败",
				"error", err, "appli_id", reqBody.CreateClubAppliId,
			)

			ctx.StatusCode(iris.StatusInternalServerError)
			ctx.Text("获取新创建的社团信息失败")
			return
		}

		ctx.JSON(iris.Map{
			"new_club_id": newClub.ClubId,
			"status":      "创建成功",
		})

		if err := h.RedisService.UploadClubInfo(newClub); err != nil {
			h.Logger.Info("转发新创建的社团信息失败",
				"error", err, "appli_id", reqBody.CreateClubAppliId,
			)

			ctx.StatusCode(iris.StatusInternalServerError)
			ctx.Text("转发新创建的社团信息失败")
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

		ctx.JSON(iris.Map{
			"status": "拒绝成功",
		})

	default:
		ctx.StatusCode(iris.StatusBadRequest)
		ctx.Text("result参数错误")
		return
	}
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
		if err := h.ClubService.ApproveAppliForUpdateClub(reqBody.UpdateAppliId); err != nil {
			h.Logger.Info("通过社团更新申请失败",
				"error", err, "appli_id", reqBody.UpdateAppliId,
			)

			ctx.StatusCode(iris.StatusInternalServerError)
			ctx.Text("通过社团更新申请失败")
			return
		}

	case "reject":
		if err := h.ClubService.RejectAppliForUpdateClub(reqBody.UpdateAppliId, reqBody.Reason); err != nil {
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

func (h *ClubAdminHandler) GetUpdateList(ctx iris.Context) {
	offset, err := ctx.URLParamInt("offset")
	if err != nil {
		h.Logger.Error("获取offset参数失败", "error", err)
		ctx.StatusCode(iris.StatusBadRequest)
		ctx.Text("获取offset参数失败")
		return
	}

	num, err := ctx.URLParamInt("num")
	if err != nil {
		h.Logger.Error("获取num参数失败", "error", err)
		ctx.StatusCode(iris.StatusBadRequest)
		ctx.Text("获取num参数失败")
		return
	}

	applis, err := h.ClubService.GetUpdateList(offset, num)
	if err != nil {
		h.Logger.Error("获取社团更新申请列表失败", "error", err)
		ctx.StatusCode(iris.StatusInternalServerError)
		ctx.Text("获取社团更新申请列表失败")
		return
	}

	var resApplis []struct {
		AppliId  int    `json:"appli_id"`
		Proposal string `json:"proposal"`
		Status   string `json:"status"`
	}
	for _, appli := range applis {
		resApplis = append(resApplis, struct {
			AppliId  int    `json:"appli_id"`
			Proposal string `json:"proposal"`
			Status   string `json:"status"`
		}{
			AppliId:  int(appli.UpdateAppliId),
			Proposal: string(appli.Proposal),
			Status:   appli.Status,
		})
	}

	ctx.JSON(resApplis)
}

func (h *ClubAdminHandler) GetCreateList(ctx iris.Context) {
	offset, err := ctx.URLParamInt("offset")
	if err != nil {
		h.Logger.Error("获取offset参数失败", "error", err)
		ctx.StatusCode(iris.StatusBadRequest)
		ctx.Text("获取offset参数失败")
		return
	}

	num, err := ctx.URLParamInt("num")
	if err != nil {
		h.Logger.Error("获取num参数失败", "error", err)
		ctx.StatusCode(iris.StatusBadRequest)
		ctx.Text("获取num参数失败")
		return
	}

	applis, err := h.ClubService.GetCreateList(offset, num)
	if err != nil {
		h.Logger.Error("获取社团创建申请列表失败", "error", err)
		ctx.StatusCode(iris.StatusInternalServerError)
		ctx.Text("获取社团创建申请列表失败")
		return
	}

	var resApplis []struct {
		AppliId  int    `json:"appli_id"`
		Proposal string `json:"proposal"`
		Status   string `json:"status"`
	}
	for _, appli := range applis {
		resApplis = append(resApplis, struct {
			AppliId  int    `json:"appli_id"`
			Proposal string `json:"proposal"`
			Status   string `json:"status"`
		}{
			AppliId:  int(appli.CreateAppliId),
			Proposal: string(appli.Proposal),
			Status:   appli.Status,
		})
	}

	ctx.JSON(resApplis)
}
