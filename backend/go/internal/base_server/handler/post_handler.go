package handler

import (
	"log/slog"
	"whuclubsynapse-server/internal/base_server/dto"
	"whuclubsynapse-server/internal/base_server/service"
	"whuclubsynapse-server/internal/shared/dbstruct"

	"github.com/kataras/iris/v12"
	"github.com/kataras/iris/v12/mvc"
)

type PostHandler struct {
	PostService service.PostService
	Logger      *slog.Logger
}

func (h *PostHandler) BeforeActivation(b mvc.BeforeActivation) {
	b.Handle("GET", "/posts/{id:int}", "GetPostList")
	b.Handle("GET", "/pinned/{id:int}", "GetPinnedPost")
	b.Handle("GET", "/comments/{id:int}", "GetPostComments")

	b.Handle("POST", "/create", "PostCreatePost")
}

func (h *PostHandler) GetPostList(ctx iris.Context, id int) {
	postNum := ctx.URLParamIntDefault("post_num", 10)
	offset := ctx.URLParamIntDefault("offset", 0)

	userRole := ctx.Values().GetString("user_claims_role")
	if userRole == "" {
		ctx.StopWithStatus(iris.StatusBadRequest)
		return
	}

	visibility := 0
	switch userRole {
	case dbstruct.ROLE_USER:
		visibility = 0
	case dbstruct.ROLE_PUBLISHER:
		visibility = 1
	case dbstruct.ROLE_ADMIN:
		visibility = 2
	}

	clubPosts, err := h.PostService.
		GetPostList(id, offset, postNum, visibility)
	if err != nil {
		h.Logger.Error("获取社团帖子列表失败",
			"error", err, "club_id", id,
		)

		ctx.StatusCode(iris.StatusBadRequest)
		ctx.Text("无法获取指定社团帖子列表")
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
			CreatedAt:    post.CreatedAt.Format("2006-01-02 15:04:05"),
		})
	}

	ctx.JSON(resClubPosts)
}

func (h *PostHandler) GetPinnedPost(ctx iris.Context, id int) {
	pinnedPost, err := h.PostService.GetPinnedPost(id)
	if err != nil {
		ctx.StatusCode(iris.StatusBadRequest)
		ctx.Text("无法获取置顶帖")
		return
	}

	ctx.JSON(dto.ClubPostBasic{
		PostId:       int(pinnedPost.PostId),
		ClubId:       int(pinnedPost.ClubId),
		Title:        pinnedPost.Title,
		AuthorId:     int(pinnedPost.UserId),
		CommentCount: int(pinnedPost.CommentCount),
		CreatedAt:    pinnedPost.CreatedAt.Format("2006-01-02 15:04:05"),
	})
}

func (h *PostHandler) GetPostComments(ctx iris.Context, id int) {
	userRole := ctx.Values().GetString("user_claims_role")
	if userRole == "" {
		ctx.StopWithStatus(iris.StatusBadRequest)
		return
	}

	visibility := 0
	switch userRole {
	case dbstruct.ROLE_USER:
		visibility = 0
	case dbstruct.ROLE_PUBLISHER:
		visibility = 1
	case dbstruct.ROLE_ADMIN:
		visibility = 2
	}

	comments, err := h.PostService.GetPostComments(id, visibility)
	if err != nil {
		h.Logger.Error("获取帖子评论失败", "error", err)

		ctx.StatusCode(iris.StatusBadRequest)
		ctx.Text("无法获取指定帖子评论")
		return
	}

	var resComments []*dto.PostComment
	for _, comment := range comments {
		resComments = append(resComments, &dto.PostComment{
			CommentId: int(comment.CommentId),
			PostId:    int(comment.PostId),
			UserId:    int(comment.UserId),
			Content:   comment.Content,
			CreatedAt: comment.CreatedAt.Format("2006-01-02 15:04:05"),
		})
	}

	ctx.JSON(resComments)
}

func (h *PostHandler) PostCreatePost(ctx iris.Context) {
	
}
