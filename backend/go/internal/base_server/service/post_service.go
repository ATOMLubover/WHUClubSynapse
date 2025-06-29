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

	CreatePost(newPost dbstruct.ClubPost,
		sender func(writer *io.PipeWriter) error) error

	// ApplyForCreatePost(tmpUrl string, newPost dbstruct.ClubPost) error
	// ApproveAppliForCreatePost(appliId int) (*dbstruct.CreatePostAppli, *dbstruct.ClubPost, error)
	// RejectAppliForCreatePost(appliId int, reason string) error

	//TransferPost(oriAppli *dbstruct.CreatePostAppli, post *dbstruct.ClubPost) error

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

// func (s *sPostService) ApplyForCreatePost(tmpUrl string, newPost dbstruct.ClubPost) error {
// 	jsonb, err := jsonbutil.ToJsonb(newPost)
// 	if err != nil {
// 		return err
// 	}

// 	appli := dbstruct.CreatePostAppli{
// 		ApplicantId:     uint(newPost.UserId),
// 		Proposal:        jsonb,
// 		DraftContentUrl: tmpUrl,
// 	}

// 	return s.createPostAppliRepo.AddCreatePostAppli(&appli)
// }

// func (s *sPostService) ApproveAppliForCreatePost(appliId int) (*dbstruct.CreatePostAppli, *dbstruct.ClubPost, error) {
// 	if appliId <= 0 {
// 		return nil, nil, errors.New("无效appliId")
// 	}

// 	ctxTmt, cancel := context.WithTimeout(context.Background(), 5*time.Second)
// 	defer cancel()

// 	var oriAppli *dbstruct.CreatePostAppli
// 	var curPost *dbstruct.ClubPost
// 	err := s.txCoordinator.RunInTransaction(ctxTmt, func(tx *gorm.DB) error {
// 		appli, err := s.createPostAppliRepo.GetAppliForUpdate(tx, appliId)
// 		if err != nil {
// 			return err
// 		}

// 		if appli.Status != "pending" {
// 			return errors.New("申请无法处理")
// 		}

// 		if err := s.createPostAppliRepo.ApproveAppli(tx, appliId); err != nil {
// 			return err
// 		}

// 		var newPost dbstruct.ClubPost
// 		if err := jsonbutil.FromJsonb(appli.Proposal, &newPost); err != nil {
// 			return err
// 		}

// 		if err := s.clubPostRepo.AddPost(&newPost); err != nil {
// 			return err
// 		}

// 		oriAppli = appli
// 		curPost = &newPost

// 		return nil
// 	})
// 	if err != nil {
// 		return nil, nil, err
// 	}

// 	return oriAppli, curPost, nil
// }

// func (s *sPostService) RejectAppliForCreatePost(appliId int, reason string) error {
// 	if appliId <= 0 {
// 		return errors.New("Invalid appliId")
// 	}

// 	return s.createPostAppliRepo.RejectAppli(appliId, reason)
// }

// func (s *sPostService) TransferPost(oriAppli *dbstruct.CreatePostAppli, post *dbstruct.ClubPost) error {
// 	oldFilePath := POST_TMP_FILE_DIR + oriAppli.DraftContentUrl
// 	newFilePath := POST_FILE_DIR +
// 		time.Now().Format("2006-01-02") + "_" +
// 		strconv.FormatInt(int64(post.PostId), 10) + ".md"

// 	if err := os.Symlink(oldFilePath, newFilePath); err != nil {
// 		return err
// 	}

// 	return nil
// }

func (s *sPostService) CreatePost(
	newPost dbstruct.ClubPost,
	sender func(writer *io.PipeWriter) error,
) error {
	if err := s.clubPostRepo.AddPost(&newPost); err != nil {
		return err
	}

	newFilePath := POST_FILE_DIR +
		time.Now().Format("2006-01-02") + "_" +
		strconv.FormatInt(int64(newPost.PostId), 10) + ".md"

	newFile, err := os.Create(newFilePath)
	if err != nil {
		return errors.New("创建对应post文件失败，需重试：" + err.Error())
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
