package repo

import (
	"errors"
	"log/slog"
	"whuclubsynapse-server/internal/shared/dbstruct"

	"gorm.io/gorm"
)

type PostCommentRepo interface {
	CreatePostComment(newComment dbstruct.ClubPostComment) error
	GetPostComments(postId int) ([]*dbstruct.ClubPostComment, error)
}

type sPostCommentRepo struct {
	database *gorm.DB
	logger   *slog.Logger
}

func CreatePostCommentRepo(
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

func (r *sPostCommentRepo) GetPostComments(postId int) ([]*dbstruct.ClubPostComment, error) {
	var comments []*dbstruct.ClubPostComment
	err := r.database.
		Where("post_id = ?", postId).
		Find(&comments).Error

	if err != nil && !errors.Is(err, gorm.ErrRecordNotFound) {
		return nil, err
	}

	return comments, nil
}
