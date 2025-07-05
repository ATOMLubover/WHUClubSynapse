package handler

import (
	"encoding/json"
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

const (
	CLUB_LOGO_DIR = "pub/club_logos/"
)

type ClubHandler struct {
	JwtFactory *jwtutil.CliamsFactory[model.UserClaims]

	ClubService service.ClubService
	PostService service.PostService

	Logger *slog.Logger
}

func (h *ClubHandler) BeforeActivation(b mvc.BeforeActivation) {
	b.Handle("GET", "/list", "GetClubList")
	b.Handle("GET", "/{id:int}/basic", "GetClubBasicInfo")
	b.Handle("GET", "/{id:int}/info", "GetClubInfo")
	b.Handle("GET", "/categories", "GetClubCategories")
	b.Handle("GET", "/category/{catId:int}", "GetClubsByCategory")
	b.Handle("GET", "/latest", "GetLatestClubs")
	b.Handle("GET", "/club_num", "GetClubNum")

	b.Handle("GET", "/my_clubs", "GetMyClubs")
	b.Handle("GET", "/my_createapplis", "GetMyCreateApplis")
	b.Handle("GET", "/my_joinapplis", "GetMyJoinApplis")
	b.Handle("GET", "/my_favorites", "GetMyFavorites")

	b.Handle("POST", "/{id:int}/join", "PostApplyForJoinClub")
	b.Handle("POST", "/create", "PostApplyForCreateClub")

	b.Handle("POST", "/favorite", "PostFavoriteClub")
	b.Handle("POST", "/unfavorite", "PostUnfavoriteClub")

	b.Handle("POST", "/quit/{id:int}", "PostQuitClub")
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
		var tags []string
		err = h.sTagsToArray(club.Tags, &tags)
		if err != nil {
			h.Logger.Error("解析社团标签失败",
				"error", err, "club", club,
			)

			ctx.StatusCode(iris.StatusInternalServerError)
			ctx.Text("无法解析社团标签")
			return
		}

		resClubList = append(resClubList, dto.ClubBasic{
			ClubId:      int(club.ClubId),
			ClubName:    club.Name,
			LeaderId:    int(club.LeaderId),
			Desc:        club.Description,
			LogoUrl:     club.LogoUrl,
			Category:    int(club.CategoryId),
			Tags:        tags,
			CreatedAt:   club.CreatedAt.Format("2006-01-02 15:04:05"),
			MemberCount: int(club.MemberCount),
		})
	}

	ctx.JSON(resClubList)
}

func (h *ClubHandler) GetClubCategories(ctx iris.Context) {
	categories, err := h.ClubService.GetClubCategories()
	if err != nil {
		h.Logger.Error("获取社团分类失败", "error", err)

		ctx.StatusCode(iris.StatusBadRequest)
		ctx.Text("无法获取社团分类")
		return
	}

	var resCategories []*dto.CategoryResponse
	for _, category := range categories {
		resCategories = append(resCategories, &dto.CategoryResponse{
			CatId: int(category.CategoryId),
			Name:  category.Name,
		})
	}

	ctx.JSON(resCategories)
}

func (h *ClubHandler) GetClubBasicInfo(ctx iris.Context, id int) {
	club, err := h.ClubService.GetClubInfo(id)
	if err != nil {
		h.Logger.Error("获取社团信息失败",
			"error", err, "club_id", id,
		)

		ctx.StatusCode(iris.StatusBadRequest)
		ctx.Text("无法获取指定社团信息")
		return
	}

	ctx.JSON(dto.ClubBasic{
		ClubId:       int(club.ClubId),
		ClubName:     club.Name,
		LeaderId:     int(club.LeaderId),
		Desc:         club.Description,
		Requirements: club.Requirements,
		LogoUrl:      club.LogoUrl,
		Category:     int(club.CategoryId),
		Tags:         nil,
		CreatedAt:    club.CreatedAt.Format("2006-01-02 15:04:05"),
	})
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
			IsPinned:     post.IsPinned,
			AuthorId:     int(post.UserId),
			CommentCount: int(post.CommentCount),
			CreatedAt:    post.CreatedAt.Format(time.DateTime),
		})
	}
	if pinnedPost != nil {
		resClubPosts = append(resClubPosts, &dto.ClubPostBasic{
			PostId:       int(pinnedPost.PostId),
			ClubId:       int(pinnedPost.ClubId),
			Title:        pinnedPost.Title,
			IsPinned:     pinnedPost.IsPinned,
			AuthorId:     int(pinnedPost.UserId),
			CommentCount: int(pinnedPost.CommentCount),
			CreatedAt:    pinnedPost.CreatedAt.Format(time.DateTime),
		})
	}

	var tags []string
	err = h.sTagsToArray(club.Tags, &tags)
	if err != nil {
		h.Logger.Error("解析社团标签失败",
			"error", err, "club", club,
		)

		ctx.StatusCode(iris.StatusInternalServerError)
		ctx.Text("无法解析社团标签")
		return
	}

	resClub := dto.ClubDetail{
		ClubBasic: dto.ClubBasic{
			ClubId:      int(club.ClubId),
			ClubName:    club.Name,
			LeaderId:    int(club.LeaderId),
			Desc:        club.Description,
			LogoUrl:     club.LogoUrl,
			Category:    int(club.CategoryId),
			Tags:        tags,
			CreatedAt:   club.CreatedAt.Format("2006-01-02 15:04:05"),
			MemberCount: int(club.MemberCount),
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
		var tags []string
		err = h.sTagsToArray(club.Tags, &tags)
		if err != nil {
			h.Logger.Error("解析社团标签失败",
				"error", err, "club", club,
			)

			ctx.StatusCode(iris.StatusInternalServerError)
			ctx.Text("无法解析社团标签")
			return
		}

		resClubsCat = append(resClubsCat, dto.ClubBasic{
			ClubId:      int(club.ClubId),
			ClubName:    club.Name,
			LeaderId:    int(club.LeaderId),
			Desc:        club.Description,
			LogoUrl:     club.LogoUrl,
			Category:    int(club.CategoryId),
			Tags:        tags,
			CreatedAt:   club.CreatedAt.Format("2006-01-02 15:04:05"),
			MemberCount: int(club.MemberCount),
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
		var tags []string
		err = h.sTagsToArray(club.Tags, &tags)
		if err != nil {
			h.Logger.Error("解析社团标签失败",
				"error", err, "club", club,
			)

			ctx.StatusCode(iris.StatusInternalServerError)
			ctx.Text("无法解析社团标签")
			return
		}

		resClubs = append(resClubs, dto.ClubBasic{
			ClubId:      int(club.ClubId),
			ClubName:    club.Name,
			LeaderId:    int(club.LeaderId),
			Desc:        club.Description,
			LogoUrl:     club.LogoUrl,
			Category:    int(club.CategoryId),
			Tags:        tags,
			CreatedAt:   club.CreatedAt.Format("2006-01-02 15:04:05"),
			MemberCount: int(club.MemberCount),
		})
	}

	ctx.JSON(resClubs)
}

func (h *ClubHandler) GetClubNum(ctx iris.Context) {
	cnt, err := h.ClubService.GetClubNum()
	if err != nil {
		h.Logger.Error("获取社团总数失败", "error", err)

		ctx.StatusCode(iris.StatusBadRequest)
		ctx.Text("获取社团总数失败")
		return
	}

	ctx.JSON(map[string]any{
		"club_num": cnt,
	})
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
		var tags []string
		err = h.sTagsToArray(club.Tags, &tags)
		if err != nil {
			h.Logger.Error("解析社团标签失败",
				"error", err, "club", club,
			)

			ctx.StatusCode(iris.StatusInternalServerError)
			ctx.Text("无法解析社团标签")
			return
		}

		resClubs = append(resClubs, dto.ClubBasic{
			ClubId:      int(club.ClubId),
			ClubName:    club.Name,
			LeaderId:    int(club.LeaderId),
			Desc:        club.Description,
			LogoUrl:     club.LogoUrl,
			Category:    int(club.CategoryId),
			Tags:        tags,
			CreatedAt:   club.CreatedAt.Format("2006-01-02 15:04:05"),
			MemberCount: int(club.MemberCount),
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
		var proposal dbstruct.Club
		err = h.sProposalToClub(appli.Proposal, &proposal)
		if err != nil {
			h.Logger.Error("解析创建社团申请失败",
				"error", err, "appli", appli,
			)

			ctx.StatusCode(iris.StatusInternalServerError)
			ctx.Text("无法解析创建社团申请")
			return
		}

		var tags []string
		err = h.sTagsToArray(proposal.Tags, &tags)
		if err != nil {
			h.Logger.Error("解析社团标签失败",
				"error", err, "club", proposal,
			)

			ctx.StatusCode(iris.StatusInternalServerError)
			ctx.Text("无法解析社团标签")
			return
		}

		resApplis = append(resApplis, &dto.CreateClubAppliResponse{
			AppliId:   int(appli.CreateAppliId),
			AppliedAt: appli.AppliedAt.Format("2006-01-02 15:04:05"),
			Proposal: dto.CreateClubAppliProposalResponse{
				Name:        proposal.Name,
				Description: proposal.Description,
				CategoryId:  int(proposal.CategoryId),
				LeaderId:    int(proposal.LeaderId),
				Tags:        tags,
			},
			Status:       appli.Status,
			RejectReason: appli.RejectedReason,
			ReviewedAt:   appli.ReviewedAt.Format("2006-01-02 15:04:05"),
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
			ClubId:       int(appli.ClubId),
			ApplicantId:  int(appli.UserId),
			Reason:       appli.ApplyReason,
			Status:       appli.Status,
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
		var tags []string
		err = h.sTagsToArray(club.Tags, &tags)
		if err != nil {
			h.Logger.Error("解析社团标签失败",
				"error", err, "club", club,
			)

			ctx.StatusCode(iris.StatusInternalServerError)
			ctx.Text("无法解析社团标签")
			return
		}

		resClubList = append(resClubList, dto.ClubBasic{
			ClubId:      int(club.ClubId),
			ClubName:    club.Name,
			LeaderId:    int(club.LeaderId),
			Category:    int(club.CategoryId),
			Tags:        tags,
			CreatedAt:   club.CreatedAt.Format(time.DateTime),
			Desc:        club.Description,
			LogoUrl:     club.LogoUrl,
			MemberCount: int(club.MemberCount),
		})
	}

	ctx.JSON(resClubList)
}

func (h *ClubHandler) PostApplyForJoinClub(ctx iris.Context, id int) {
	var reqBody dto.JoinClubAppliRequest
	if err := ctx.ReadJSON(&reqBody); err != nil {
		h.Logger.Error("请求格式错误", "error", err)

		ctx.StatusCode(iris.StatusBadRequest)
		ctx.Text("请求格式错误")
		return
	}

	userId, err := ctx.Values().GetInt("user_claims_user_id")
	if err != nil {
		h.Logger.Error("无法获取用户ID", "error", err)

		ctx.StopWithStatus(iris.StatusBadRequest)
		return
	}

	if err := h.ClubService.ApplyForJoinClub(
		uint(userId), uint(id),
		reqBody.Reason,
	); err != nil {
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
	userId, err := ctx.Values().GetInt("user_claims_user_id")
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

	var tags []byte
	if len(reqBody.Tags) != 0 {
		tags, err = json.Marshal(reqBody.Tags)
		if err != nil {
			h.Logger.Error("反序列化社团标签失败",
				"error", err, "tags", reqBody.Tags,
			)

			ctx.StatusCode(iris.StatusInternalServerError)
			ctx.Text("无法反序列化社团标签")
			return
		}
	}

	err = h.ClubService.ApplyForCreateClub(dbstruct.Club{
		Name:         reqBody.Name,
		Description:  reqBody.Desc,
		LeaderId:     uint(userId),
		CategoryId:   uint(reqBody.CategoryId),
		Requirements: reqBody.Requirements,
		Tags:         tags,
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

func (h *ClubHandler) PostFavoriteClub(ctx iris.Context) {
	var reqBody dto.FavoriteClubRequest
	if err := ctx.ReadJSON(&reqBody); err != nil {
		h.Logger.Info("收藏社团请求格式错误", "error", err)

		ctx.StatusCode(iris.StatusBadRequest)
		ctx.Text("请求格式错误")
		return
	}

	userId, err := ctx.Values().GetInt("user_claims_user_id")
	if err != nil {
		h.Logger.Info("获取用户ID失败", "error", err)

		ctx.StatusCode(iris.StatusBadRequest)
		ctx.Text("用户ID获取失败")
		return
	}

	if err := h.ClubService.FavouriteClub(userId, reqBody.ClubId); err != nil {
		h.Logger.Info("收藏社团失败", "error", err)

		ctx.StatusCode(iris.StatusInternalServerError)
		ctx.Text("收藏社团失败")
		return
	}

	ctx.Text("收藏社团成功")
}

func (h *ClubHandler) PostUnfavoriteClub(ctx iris.Context) {
	var reqBody dto.UnfavoriteClubRequest
	if err := ctx.ReadJSON(&reqBody); err != nil {
		h.Logger.Info("取消收藏社团请求格式错误", "error", err)

		ctx.StatusCode(iris.StatusBadRequest)
		ctx.Text("请求格式错误")
		return
	}

	userId, err := ctx.Values().GetInt("user_claims_user_id")
	if err != nil {
		h.Logger.Info("获取用户ID失败", "error", err)

		ctx.StatusCode(iris.StatusBadRequest)
		ctx.Text("用户ID获取失败")
		return
	}

	if err := h.ClubService.UnfavouriteClub(userId, reqBody.ClubId); err != nil {
		h.Logger.Info("取消收藏社团失败", "error", err)

		ctx.StatusCode(iris.StatusBadRequest)
		ctx.Text("取消收藏社团失败")
		return
	}

	ctx.Text("取消收藏社团成功")
}

func (h *ClubHandler) sTagsToArray(raw []byte, v *[]string) error {
	if len(raw) == 0 {
		return nil
	}

	if err := json.Unmarshal(raw, v); err != nil {
		h.Logger.Error("解析标签失败", "error", err)
		return err
	}

	return nil
}

func (h *ClubHandler) sProposalToClub(raw []byte, v *dbstruct.Club) error {
	if len(raw) == 0 {
		return nil
	}

	if err := json.Unmarshal(raw, v); err != nil {
		h.Logger.Error("解析社团申请proposal失败", "error", err)
		return err
	}

	return nil
}

func (h *ClubHandler) PostQuitClub(ctx iris.Context, id int) {
	userId, err := ctx.Values().GetInt("user_claims_user_id")
	if err != nil {
		h.Logger.Error("获取用户ID失败", "error", err)

		ctx.StatusCode(iris.StatusBadRequest)
		ctx.Text("用户ID无效")
		return
	}

	clubs, err := h.ClubService.GetClubListByUserId(userId)
	if err != nil {
		h.Logger.Error("获取用户社团列表失败",
			"error", err, "user_id", userId,
		)

		ctx.StatusCode(iris.StatusBadRequest)
		ctx.Text("无法获取用户社团列表")
		return
	}

	inClub := false
	for _, club := range clubs {
		if club.LeaderId == uint(userId) &&
			club.ClubId == uint(id) {
			h.Logger.Error("用户是社团的负责人，无法退出",
				"user_id", userId, "club_id", id,
			)
			ctx.StatusCode(iris.StatusBadRequest)
			ctx.Text("用户是社团的负责人，无法退出")
			return
		}

		if club.ClubId == uint(id) {
			inClub = true
			break
		}
	}
	if !inClub {
		h.Logger.Error("用户不可以退出该社团",
			"user_id", userId, "club_id", id,
		)
		ctx.StatusCode(iris.StatusBadRequest)
		ctx.Text("用户不可以退出该社团")
		return
	}

	if err := h.ClubService.QuitClub(id, userId); err != nil {
		h.Logger.Error("退出社团失败",
			"error", err, "club_id", id, "user_id", userId,
		)

		ctx.StatusCode(iris.StatusBadRequest)
		ctx.Text("无法退出社团")
		return
	}

	ctx.Text("退出社团成功")
}
