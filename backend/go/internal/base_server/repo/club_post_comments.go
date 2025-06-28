package repo

import (
	"log/slog"
	"whuclubsynapse-server/internal/shared/dbstruct"

	"gorm.io/gorm"
)

type PostCommentRepo interface {
    CreatePostComment(newComment dbstruct.ClubPostComment) error
    GetPostComments(postId, visibility int) ([]*dbstruct.ClubPostComment, error)
}

type sPostCommentRepo struct {
	database *gorm.DB
	logger   *slog.Logger
}

func NewPostCommentRepo(
	database *gorm.DB,
	logger *slog.Logger,
) PostCommentRepo {
	return &sPostCommentRepo{
		database: database,
		logger:   logger,
	}
}

func (r *sPostCommentRepo) CreatePostComment(newComment dbstruct.ClubPostComment) error {
	return r.database.Create(&newComment).Error
}

func (r *sPostCommentRepo) GetPostComments(postId, visibility int) ([]*dbstruct.ClubPostComment, error) {
	var comments []*dbstruct.ClubPostComment
	err := r.database.
		Where("post_id = ? AND visibility <= ?", postId, visibility).
		Find(&comments).Error
	return comments, err
}
