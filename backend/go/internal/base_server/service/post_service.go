package service

import (
	"errors"
	"io"
	"log/slog"
	"os"
	"strconv"
	"time"
	"whuclubsynapse-server/internal/base_server/repo"
	"whuclubsynapse-server/internal/shared/dbstruct"
)

const (
	POST_FILE_DIR     = "pub/post_files/"
	POST_TMP_FILE_DIR = "pub/post_tmp_files/"
)

type PostService interface {
	GetLatestPosts(clubId, num, visibility int) ([]*dbstruct.ClubPost, error)
	GetPostList(clubId, offset, num, visibility int) ([]*dbstruct.ClubPost, error)
	GetPinnedPost(clubId int) (*dbstruct.ClubPost, error)
	GetPostsByUserId(userId int) ([]*dbstruct.ClubPost, error)

	CreatePost(newPost *dbstruct.ClubPost,
		sender func(writer *io.PipeWriter) error) error

	CreatePostComment(newComment dbstruct.ClubPostComment) error
	GetPostComments(postId, visibility int) ([]*dbstruct.ClubPostComment, error)

	BanPost(role string, postId int) error
	PinPost(postId int) error
}

type sPostService struct {
	clubPostRepo repo.ClubPostRepo
	//createPostAppliRepo repo.CreatePostAppliRepo
	postCommentRepo repo.PostCommentRepo

	txCoordinator repo.TransactionCoordinator

	logger *slog.Logger
}

func CreatePostService(
	clubPostRepo repo.ClubPostRepo,
	//createPostAppliRepo repo.CreatePostAppliRepo,
	postCommentRepo repo.PostCommentRepo,

	txCoordinator repo.TransactionCoordinator,

	logger *slog.Logger,
) PostService {
	return &sPostService{
		clubPostRepo: clubPostRepo,
		//createPostAppliRepo: createPostAppliRepo,
		postCommentRepo: postCommentRepo,

		logger: logger,
	}
}

func (s *sPostService) GetLatestPosts(clubId, num, visibility int) ([]*dbstruct.ClubPost, error) {
	return s.clubPostRepo.GetClubPostList(clubId, 0, num, visibility)
}

func (s *sPostService) GetPostList(clubId, offset, num, visibility int) ([]*dbstruct.ClubPost, error) {
	return s.clubPostRepo.GetClubPostList(clubId, offset, num, visibility)
}

func (s *sPostService) ChangePostVisibility(postId, visibility int) error {
	return s.clubPostRepo.ChangePostVisibility(postId, visibility)
}

func (s *sPostService) GetPinnedPost(clubId int) (*dbstruct.ClubPost, error) {
	return s.clubPostRepo.GetPinnedPost(clubId)
}

func (s *sPostService) GetPostsByUserId(userId int) ([]*dbstruct.ClubPost, error) {
	return s.clubPostRepo.GetPostsByUserId(userId)
}

func (s *sPostService) CreatePost(
	newPost *dbstruct.ClubPost,
	sender func(writer *io.PipeWriter) error,
) error {
	if err := s.clubPostRepo.AddPost(newPost); err != nil {
		return err
	}

	newFilePath := POST_FILE_DIR +
		time.Now().Format("2006-01-02") + "_" +
		strconv.FormatInt(int64(newPost.PostId), 10) + ".md"

	newFile, err := os.Create(newFilePath)
	if err != nil {
		return errors.New("创建对应post文件失败，需重试：" + err.Error() +
			"（path: " + newFilePath + "）")
	}

	defer newFile.Close()

	reader, writer := io.Pipe()
	defer reader.Close()

	go sender(writer)

	if _, err := io.CopyBuffer(
		newFile, reader,
		nil); err != nil {
		if err != io.EOF {
			return errors.New("写入文件失败，需重试：" + err.Error())
		}
		return nil
	}

	if err := s.clubPostRepo.UpdatePostUrl(int(newPost.PostId), newFilePath); err != nil {
		return errors.New("更新post URI失败，需重试：" + err.Error())
	}

	newPost.ContentUrl = newFilePath

	return nil
}

func (s *sPostService) CreatePostComment(newComment dbstruct.ClubPostComment) error {
	return s.postCommentRepo.CreatePostComment(newComment)
}

func (s *sPostService) GetPostComments(postId, visibility int) ([]*dbstruct.ClubPostComment, error) {
	return s.postCommentRepo.GetPostComments(postId, visibility)
}

func (s *sPostService) BanPost(role string, postId int) error {
	switch role {
	case dbstruct.ROLE_ADMIN:
		return s.clubPostRepo.ChangePostVisibility(postId, 2)

	case dbstruct.ROLE_CLUB_LEADER:
		return s.clubPostRepo.ChangePostVisibility(postId, 1)

	default:
		return errors.New("未知权限：" + role)
	}
}

func (s *sPostService) PinPost(postId int) error {
	return s.clubPostRepo.PinPost(postId)
}
