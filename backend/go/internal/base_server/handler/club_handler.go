package handler

import (
	"log/slog"
	"time"
	"whuclubsynapse-server/internal/base_server/dto"
	"whuclubsynapse-server/internal/base_server/model"
	"whuclubsynapse-server/internal/base_server/service"
	"whuclubsynapse-server/internal/shared/dbstruct"
	"whuclubsynapse-server/internal/shared/jwtutil"

	"github.com/kataras/iris/v12"
	"github.com/kataras/iris/v12/mvc"
)

type ClubHandler struct {
	JwtFactory *jwtutil.CliamsFactory[model.UserClaims]

	ClubService service.ClubService
	PostService service.PostService

	Logger *slog.Logger
}

func (h *ClubHandler) BeforeActivation(b mvc.BeforeActivation) {
	b.Handle("GET", "/list", "GetClubList")
	b.Handle("GET", "/{id:int}/info", "GetClubInfo")
	b.Handle("GET", "/category/{catId:int}", "GetClubsByCategory")
	b.Handle("GET", "/latest", "GetLatestClubs")

	b.Handle("GET", "/my_clubs", "GetMyClubs")
	b.Handle("GET", "/my_createapplis", "GetMyCreateApplis")
	b.Handle("GET", "/my_joinapplis", "GetMyJoinApplis")
	b.Handle("GET", "/my_favorites", "GetMyFavorites")

	b.Handle("POST", "/{id:int}/join", "PostApplyForJoinClub")
	b.Handle("POST", "/create", "PostApplyForCreateClub")
}

func (h *ClubHandler) GetClubList(ctx iris.Context) {
	offset := ctx.URLParamIntDefault("offset", 0)
	num := ctx.URLParamIntDefault("num", 10)

	clubs, err := h.ClubService.GetClubList(offset, num)
	if err != nil {
		h.Logger.Error("获取社团列表失败",
			"error", err, "offset", offset, "num", num,
		)

		ctx.StatusCode(iris.StatusBadRequest)
		ctx.Text("无法获取指定范围社团列表")
		return
	}

	var resClubList []dto.ClubBasic

	for _, club := range clubs {
		resClubList = append(resClubList, dto.ClubBasic{
			ClubId:    int(club.ClubId),
			ClubName:  club.Name,
			Desc:      club.Description,
			LogoUrl:   club.LogoUrl,
			Category:  int(club.CategoryId),
			CreatedAt: club.CreatedAt.Format("2006-01-02 15:04:05"),
		})
	}

	ctx.JSON(resClubList)
}

func (h *ClubHandler) GetClubInfo(ctx iris.Context, id int) {
	club, err := h.ClubService.GetClubInfo(id)
	if err != nil {
		h.Logger.Error("获取社团信息失败",
			"error", err, "club_id", id,
		)

		ctx.StatusCode(iris.StatusBadRequest)
		ctx.Text("无法获取指定社团信息")
		return
	}

	clubMembers, err := h.ClubService.GetMemberList(id)
	if err != nil {
		h.Logger.Error("获取社团成员列表失败",
			"error", err, "club_id", id,
		)

		ctx.StatusCode(iris.StatusBadRequest)
		ctx.Text("无法获取指定社团成员列表")
		return
	}

	var resClubMems []*dto.ClubMember

	for _, member := range clubMembers {
		resClubMems = append(resClubMems, &dto.ClubMember{
			ClubId:     int(member.ClubId),
			MemberId:   int(member.UserId),
			RoleInClub: member.RoleInClub,
			JoinedAt:   member.JoinedAt.Format(time.DateTime),
			LastActive: member.LastActive.Format(time.DateTime),
		})
	}

	postNum := ctx.URLParamIntDefault("post_num", 5)

	clubPosts, err := h.PostService.GetPostList(id, 0, postNum, 0)
	if err != nil {
		h.Logger.Error("获取社团帖子列表失败",
			"error", err, "club_id", id,
		)

		ctx.StatusCode(iris.StatusBadRequest)
		ctx.Text("无法获取指定社团帖子列表")
		return
	}

	pinnedPost, err := h.PostService.GetPinnedPost(id)
	if err != nil {
		h.Logger.Error("获取社团置顶帖子失败",
			"error", err, "club_id", id,
		)

		ctx.StatusCode(iris.StatusBadRequest)
		ctx.Text("无法获取指定社团置顶帖子")
		return
	}

	var resClubPosts []*dto.ClubPostBasic

	for _, post := range clubPosts {
		resClubPosts = append(resClubPosts, &dto.ClubPostBasic{
			PostId:       int(post.PostId),
			ClubId:       int(post.ClubId),
			Title:        post.Title,
			AuthorId:     int(post.UserId),
			CommentCount: int(post.CommentCount),
			CreatedAt:    post.CreatedAt.Format(time.DateTime),
		})
	}
	resClubPosts = append(resClubPosts, &dto.ClubPostBasic{
		PostId:       int(pinnedPost.PostId),
		ClubId:       int(pinnedPost.ClubId),
		Title:        pinnedPost.Title,
		AuthorId:     int(pinnedPost.UserId),
		CommentCount: int(pinnedPost.CommentCount),
		CreatedAt:    pinnedPost.CreatedAt.Format(time.DateTime),
	})

	resClub := dto.ClubDetail{
		ClubBasic: dto.ClubBasic{
			ClubId:    int(club.ClubId),
			ClubName:  club.Name,
			Desc:      club.Description,
			LogoUrl:   club.LogoUrl,
			Category:  int(club.CategoryId),
			CreatedAt: club.CreatedAt.Format("2006-01-02 15:04:05"),
		},
		Members: resClubMems,
		Posts:   resClubPosts,
	}

	ctx.JSON(resClub)
}

func (h *ClubHandler) GetClubsByCategory(ctx iris.Context, catId int) {
	clubs, err := h.ClubService.GetClubsByCategory(catId)
	if err != nil {
		h.Logger.Error("获取特别分类社团列表失败",
			"error", err, "cat_id", catId,
		)

		ctx.StatusCode(iris.StatusBadRequest)
		ctx.Text("无法获取指定分类社团列表")
		return
	}

	var resClubsCat []dto.ClubBasic

	for _, club := range clubs {
		resClubsCat = append(resClubsCat, dto.ClubBasic{
			ClubId:    int(club.ClubId),
			ClubName:  club.Name,
			Desc:      club.Description,
			LogoUrl:   club.LogoUrl,
			Category:  int(club.CategoryId),
			CreatedAt: club.CreatedAt.Format("2006-01-02 15:04:05"),
		})
	}

	ctx.JSON(resClubsCat)
}

func (h *ClubHandler) GetLatestClubs(ctx iris.Context) {
	clubs, err := h.ClubService.GetLatestClubs()
	if err != nil {
		h.Logger.Error("获取最新社团列表失败",
			"error", err,
		)

		ctx.StatusCode(iris.StatusBadRequest)
		ctx.Text("无法获取最新社团列表")
		return
	}

	var resClubs []dto.ClubBasic

	for _, club := range clubs {
		resClubs = append(resClubs, dto.ClubBasic{
			ClubId:    int(club.ClubId),
			ClubName:  club.Name,
			Desc:      club.Description,
			LogoUrl:   club.LogoUrl,
			Category:  int(club.CategoryId),
			CreatedAt: club.CreatedAt.Format("2006-01-02 15:04:05"),
		})
	}

	ctx.JSON(resClubs)
}

func (h *ClubHandler) GetMyClubs(ctx iris.Context) {
	userId, err := ctx.Values().GetInt("user_claims_user_id")
	if err != nil {
		h.Logger.Error("无法获取用户ID", "error", err)

		ctx.StopWithStatus(iris.StatusBadRequest)
		return
	}

	clubs, err := h.ClubService.GetClubListByUserId(userId)
	if err != nil {
		h.Logger.Error("获取用户的社团列表失败",
			"error", err, "user_id", userId,
		)

		ctx.StatusCode(iris.StatusBadRequest)
		ctx.Text("无法获取用户社团列表")
		return
	}

	var resClubs []dto.ClubBasic

	for _, club := range clubs {
		resClubs = append(resClubs, dto.ClubBasic{
			ClubId:    int(club.ClubId),
			ClubName:  club.Name,
			Desc:      club.Description,
			LogoUrl:   club.LogoUrl,
			Category:  int(club.CategoryId),
			CreatedAt: club.CreatedAt.Format("2006-01-02 15:04:05"),
		})
	}

	ctx.JSON(resClubs)
}

func (h *ClubHandler) GetMyCreateApplis(ctx iris.Context) {
	userId, err := ctx.Values().GetInt("user_claims_user_id")
	if err != nil {
		ctx.StatusCode(iris.StatusBadRequest)
		ctx.Text("获取用户ID失败")
		return
	}

	applis, err := h.ClubService.GetUserCreateApplis(userId)
	if err != nil {
		h.Logger.Error(
			"获取用户创建社团申请列表失败",
			"error", err, "user_id", userId,
		)

		ctx.StatusCode(iris.StatusBadRequest)
		ctx.Text("获取用户创建社团申请列表失败")
		return
	}

	var resApplis []*dto.CreateClubAppliResponse
	for _, appli := range applis {
		resApplis = append(resApplis, &dto.CreateClubAppliResponse{
			AppliId:      int(appli.CreateAppliId),
			AppliedAt:    appli.AppliedAt.Format(time.RFC3339),
			RejectReason: appli.RejectedReason,
			ReviewedAt:   appli.ReviewedAt.Format(time.RFC3339),
		})
	}

	ctx.JSON(resApplis)
}

func (h *ClubHandler) GetMyJoinApplis(ctx iris.Context) {
	userId, err := ctx.Values().GetInt("user_claims_user_id")
	if err != nil {
		ctx.StatusCode(iris.StatusBadRequest)
		ctx.Text("获取用户ID失败")
		return
	}

	applis, err := h.ClubService.GetUserJoinApplis(userId)
	if err != nil {
		h.Logger.Error(
			"获取用户加入社团申请列表失败",
			"error", err, "user_id", userId,
		)

		ctx.StatusCode(iris.StatusBadRequest)
		ctx.Text("获取用户加入社团申请列表失败")
		return
	}

	var resApplis []*dto.JoinClubAppliResponse
	for _, appli := range applis {
		resApplis = append(resApplis, &dto.JoinClubAppliResponse{
			AppliId:      int(appli.JoinAppliId),
			AppliedAt:    appli.AppliedAt.Format(time.RFC3339),
			RejectReason: appli.RejectedReason,
			ReviewedAt:   appli.ReviewedAt.Format(time.RFC3339),
		})
	}

	ctx.JSON(resApplis)
}

func (h *ClubHandler) GetMyFavorites(ctx iris.Context) {
	userId, err := ctx.Values().GetInt("user_claims_user_id")
	if err != nil {
		ctx.StatusCode(iris.StatusBadRequest)
		ctx.Text("获取用户ID失败")
		return
	}

	clubs, err := h.ClubService.GetFavoriteClubs(userId)
	if err != nil {
		h.Logger.Info("获取收藏社团列表失败",
			"error", err, "user_id", userId,
		)

		ctx.StatusCode(iris.StatusBadRequest)
		ctx.Text("无法获取收藏社团列表")
		return
	}

	var resClubList []dto.ClubBasic
	for _, club := range clubs {
		resClubList = append(resClubList, dto.ClubBasic{
			ClubId:    int(club.ClubId),
			ClubName:  club.Name,
			Category:  int(club.CategoryId),
			CreatedAt: club.CreatedAt.Format(time.DateTime),
			Desc:      club.Description,
			LogoUrl:   club.LogoUrl,
		})
	}

	ctx.JSON(resClubList)
}

func (h *ClubHandler) PostApplyForJoinClub(ctx iris.Context, id int) {
	userId, err := ctx.Values().GetInt("user_claims_user_id")
	if err != nil {
		h.Logger.Error("无法获取用户ID", "error", err)

		ctx.StopWithStatus(iris.StatusBadRequest)
		return
	}

	if err := h.ClubService.ApplyForJoinClub(
		uint(userId), uint(id)); err != nil {
		h.Logger.Error("申请加入社团失败",
			"error", err, "user_id", userId, "club_id", id,
		)

		ctx.StatusCode(iris.StatusBadRequest)
		ctx.Text("无法申请加入社团")
		return
	}

	ctx.Text("加入社团申请成功")
}

func (h *ClubHandler) PostApplyForCreateClub(ctx iris.Context) {
	userId, err := ctx.Values().GetInt("user_id")
	if err != nil {
		h.Logger.Error("获取上下文用户ID失败",
			"error", err,
		)

		ctx.StatusCode(iris.StatusBadRequest)
		ctx.Text("无法获取用户ID")
		return
	}

	var reqBody dto.CreateClubAppliRequest
	if err := ctx.ReadJSON(&reqBody); err != nil {
		h.Logger.Error("请求格式错误", "error", err)

		ctx.StatusCode(iris.StatusBadRequest)
		ctx.Text("请求格式错误")
		return
	}

	err = h.ClubService.ApplyForCreateClub(dbstruct.Club{
		Name:        reqBody.Name,
		Description: reqBody.Desc,
		LeaderId:    uint(userId),
	})
	if err != nil {
		h.Logger.Error("申请创建社团失败",
			"error", err, "user_id", userId,
		)

		ctx.StatusCode(iris.StatusBadRequest)
		ctx.Text("无法申请创建社团")
		return
	}

	ctx.Text("创建社团申请成功")
}
