package handler

import (
	"io"
	"log/slog"
	"strconv"
	"strings"
	"whuclubsynapse-server/internal/base_server/dto"
	"whuclubsynapse-server/internal/base_server/redisimpl"
	"whuclubsynapse-server/internal/base_server/service"
	"whuclubsynapse-server/internal/shared/dbstruct"

	"github.com/kataras/iris/v12"
	"github.com/kataras/iris/v12/mvc"
)

type PostHandler struct {
	PostService  service.PostService
	RedisService redisimpl.RedisClientService

	Logger *slog.Logger
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
	userId, err := ctx.Values().GetInt("user_claims_user_id")
	if err != nil {
		ctx.StatusCode(iris.StatusBadRequest)
		ctx.Text("用户ID获取失败")
		return
	}

	title := ctx.PostValue("title")
	clubIdStr := ctx.PostValue("club_id")
	content := ctx.PostValue("content")

	clubId, err := strconv.Atoi(clubIdStr)
	if err != nil {
		h.Logger.Error("转化社团ID失败",
			"error", err,
		)

		ctx.StatusCode(iris.StatusBadRequest)
		ctx.Text("转化社团ID失败")
		return
	}

	newPost := dbstruct.ClubPost{
		UserId: uint(userId),
		ClubId: uint(clubId),
		Title:  title,
	}

	if err := h.PostService.CreatePost(
		&newPost, func(writer *io.PipeWriter) error {
			defer writer.Close()

			_, err := io.Copy(writer, strings.NewReader(content))
			return err
		}); err != nil {
		h.Logger.Error("创建帖子失败",
			"error", err,
		)

		ctx.StatusCode(iris.StatusBadRequest)
		ctx.Text("创建帖子失败")
		return
	}

	if err := h.RedisService.UploadPostInfo(&newPost); err != nil {
		h.Logger.Error("上传帖子信息失败",
			"error", err, "post_id", newPost.PostId, 
			"path", newPost.ContentUrl,
		)
	}

	ctx.Text("创建帖子成功")
}
