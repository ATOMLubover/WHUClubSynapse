package handler

import (
	"encoding/json"
	"io"
	"log/slog"
	"os"
	"path/filepath"
	"strconv"
	"whuclubsynapse-server/internal/base_server/dto"
	"whuclubsynapse-server/internal/base_server/model"
	"whuclubsynapse-server/internal/base_server/service"
	"whuclubsynapse-server/internal/shared/dbstruct"
	"whuclubsynapse-server/internal/shared/jwtutil"

	"github.com/kataras/iris/v12"
	"github.com/kataras/iris/v12/mvc"
	"gorm.io/datatypes"
)

type ClubPubHandler struct {
	JwtFactory *jwtutil.CliamsFactory[model.UserClaims]

	ClubService service.ClubService

	Logger *slog.Logger
}

func (h *ClubPubHandler) BeforeActivation(b mvc.BeforeActivation) {
	b.Handle("GET", "/join_applis/{id:int}", "GetJoinApplisForClub")
	b.Handle("GET", "/my_update_applis", "GetMyUpdateApplis")

	b.Handle("POST", "/update/{id:int}", "PostApplyForUpdateClubInfo")
	b.Handle("POST", "/update_logo/{id:int}", "PostUploadLogo")
	b.Handle("POST", "/assemble/{id:int}", "PostAssembleClub")

	b.Handle("PUT", "/proc_join", "PutProcAppliForJoinClub")
}

func (h *ClubPubHandler) PostApplyForUpdateClubInfo(ctx iris.Context, id int) {
	userId, err := ctx.Values().GetInt("user_claims_user_id")
	if err != nil {
		h.Logger.Error("获取用户ID失败", "error", err)

		ctx.StatusCode(iris.StatusBadRequest)
		ctx.Text("用户ID无效")
		return
	}

	var reqBody dto.UpdateClubInfoRequest
	if err := ctx.ReadJSON(&reqBody); err != nil {
		h.Logger.Error("请求格式错误", "error", err)

		ctx.StatusCode(iris.StatusBadRequest)
		ctx.Text("请求格式错误")
		return
	}

	var jsonbData datatypes.JSON

	if len(reqBody.Tags) > 0 {
		data, err := json.Marshal(reqBody.Tags)
		if err != nil {
			h.Logger.Error("序列化标签失败", "error", err)

			ctx.StatusCode(iris.StatusInternalServerError)
			ctx.Text("无法序列化标签")
			return
		}
		jsonbData = datatypes.JSON(data)
	}

	err = h.ClubService.ApplyForUpdateClub(
		dbstruct.Club{
			ClubId:       uint(id),
			LeaderId:     uint(userId),
			Name:         reqBody.Name,
			Description:  reqBody.Desc,
			Requirements: reqBody.Requirements,
			CategoryId:   uint(reqBody.CatogoryId),
			Tags:         jsonbData,
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

func (h *ClubPubHandler) PostUploadLogo(ctx iris.Context, id int) {
	userRole := ctx.Values().GetString("user_claims_role")
	if userRole == "" {
		ctx.StatusCode(iris.StatusForbidden)
		return
	}

	userId, err := ctx.Values().GetInt("user_claims_user_id")
	if err != nil {
		ctx.StatusCode(iris.StatusBadRequest)
		return
	}

	clubs, err := h.ClubService.GetClubListByUserId(userId)
	isLeader := false
	for _, club := range clubs {
		if int(club.ClubId) != id {
			continue
		}

		if club.LeaderId == uint(userId) {
			isLeader = true
			break
		}
	}

	if !isLeader {
		ctx.StatusCode(iris.StatusForbidden)
		return
	}

	file, _, err := ctx.FormFile("logo")
	if err != nil {
		ctx.StatusCode(iris.StatusBadRequest)
		ctx.Text("未成功获取上传的logo文件")
		return
	}

	defer file.Close()

	if err := os.MkdirAll(CLUB_LOGO_DIR, os.ModePerm); err != nil {
		ctx.StatusCode(iris.StatusInternalServerError)
		ctx.Text("目录创建失败")
		return
	}

	filePath := filepath.Join(CLUB_LOGO_DIR, "_"+strconv.Itoa(id))
	dst, err := os.Create(filePath)
	if err != nil {
		ctx.StatusCode(iris.StatusInternalServerError)
		ctx.Text("文件创建失败")
		return
	}
	defer dst.Close()

	if _, err := io.Copy(dst, file); err != nil {
		ctx.StatusCode(iris.StatusInternalServerError)
		ctx.Text("文件保存失败")
		return
	}

	ctx.JSON(iris.Map{"status": "文件上传成功", "path": filePath})
}

func (h *ClubPubHandler) PostAssembleClub(ctx iris.Context, id int) {
	userRole := ctx.Values().GetString("user_claims_user_role")
	if userRole == "" ||
		userRole != dbstruct.ROLE_ADMIN &&
			userRole != dbstruct.ROLE_CLUB_LEADER {
		h.Logger.Error("用户权限错误", "role", userRole)

		ctx.StatusCode(iris.StatusForbidden)
		return
	}

	if err := h.ClubService.DissambleClub(id); err != nil {
		h.Logger.Error("解散社团失败", "error", err, "club_id", id)

		ctx.StatusCode(iris.StatusInternalServerError)
		ctx.Text("无法解散社团")
		return
	}

	ctx.Text("社团解散成功")
}

func (h *ClubPubHandler) GetMyUpdateApplis(ctx iris.Context) {
	userId, err := ctx.Values().GetInt("user_claims_user_id")
	if err != nil {
		h.Logger.Error("获取用户ID失败", "error", err)

		ctx.StatusCode(iris.StatusBadRequest)
		ctx.Text("用户ID无效")
		return
	}

	applis, err := h.ClubService.GetUpdateApplisForUser(userId)
	if err != nil {
		h.Logger.Error("获取社团更新申请列表失败", "error", err)

		ctx.StatusCode(iris.StatusInternalServerError)
		ctx.Text("无法获取社团更新申请列表")
		return
	}

	var resApplis []string
	for _, appli := range applis {
		resApplis = append(resApplis, string(appli.Proposal))
	}

	ctx.JSON(resApplis)
}
