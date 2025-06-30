package redisimpl

import (
	"context"
	"encoding/json"
	"errors"
	"io"
	"log/slog"
	"os"
	"strconv"
	"time"
	"whuclubsynapse-server/internal/base_server/baseconfig"
	"whuclubsynapse-server/internal/shared/dbstruct"
	"whuclubsynapse-server/internal/shared/rediscli"

	"github.com/redis/go-redis/v9"
)

const (
	kVrfCodePrefix = "vrfcode_"
)

type RedisClientService interface {
	CheckVrfcodeExisting(email string) bool
	ValidateRegVrfcode(email, vrfcode string) bool
	UploadClubInfo(clubInfo *dbstruct.Club) error
	UploadPostInfo(postInfo *dbstruct.ClubPost) error
}

type sRedisClientService struct {
	client *rediscli.RedisClient

	logger *slog.Logger
}

func NewRedisClientService(
	cfg *baseconfig.Config,
	logger *slog.Logger,
) RedisClientService {
	client := rediscli.NewRedisClient(
		cfg.RedisHost+":"+strconv.FormatUint(uint64(cfg.RedisPort), 10),
		cfg.RedisPassword,
		cfg.RedisMaxConn,
		cfg.RedisMinIdle,
		cfg.RedisMaxRetries,
	)
	return &sRedisClientService{
		client: client,
		logger: logger,
	}
}

func (s *sRedisClientService) CheckVrfcodeExisting(email string) bool {
	ctx, cancel := context.WithTimeout(context.Background(), 7*time.Second)
	defer cancel()

	_, err := s.client.Inst().Get(ctx, kVrfCodePrefix+email).Result()
	if err == redis.Nil {
		return false
	}
	if err != nil {
		s.logger.Error("Redis Get操作异常", "error", err)
		return false
	}

	return true
}

func (s *sRedisClientService) ValidateRegVrfcode(email, vrfcode string) bool {
	ctx, cancel := context.WithTimeout(context.Background(), 7*time.Second)
	defer cancel()

	redisVrfcode, err := s.client.Inst().Get(ctx, kVrfCodePrefix+email).Result()
	if err == redis.Nil {
		return false
	}
	if err != nil {
		s.logger.Error("Redis操作异常", "error", err)
		return false
	}

	if redisVrfcode != vrfcode {
		return false
	}

	return true
}

func (s *sRedisClientService) UploadClubInfo(clubInfo *dbstruct.Club) error {
	s.logger.Debug("上传社团信息", "club", clubInfo)

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	strClubId := strconv.Itoa(int(clubInfo.ClubId))
	if strClubId == "" {
		return errors.New("无法转化club_id为字符串")
	}

	metadataJson, err := json.Marshal(map[string]any{})
	if err != nil {
		return err
	}

	cmd := s.client.Inst().XAdd(ctx, &redis.XAddArgs{
		Stream: "rag_sync_stream",
		Values: map[string]any{
			"source_id": "club_id::" + strClubId,
			"content":   clubInfo.Description,
			"metadata":  string(metadataJson),
		},
	})

	msgId, err := cmd.Result()
	if err != nil {
		s.logger.Error("Redis操作异常", "error", err)
		return err
	}

	s.logger.Info("上传社团信息成功", "msg_id", msgId)

	return nil
}

func (s *sRedisClientService) UploadPostInfo(postInfo *dbstruct.ClubPost) error {
	s.logger.Debug("上传帖子信息", "post", postInfo)

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	strPostId := strconv.Itoa(int(postInfo.PostId))
	if strPostId == "" {
		return errors.New("无法转化post_id为字符串")
	}

	postFile, err := os.Open(postInfo.ContentUrl)
	if err != nil {
		return err
	}
	defer postFile.Close()

	content, err := io.ReadAll(postFile)
	if err != nil {
		return err
	}

	metadataJson, err := json.Marshal(map[string]any{})
	if err != nil {
		return err
	}

	cmd := s.client.Inst().XAdd(ctx, &redis.XAddArgs{
		Stream: "rag_sync_stream",
		Values: map[string]any{
			"source_id": "post_id::" + strPostId,
			"content":   string(content),
			"metadata":  string(metadataJson),
		},
	})

	msgId, err := cmd.Result()
	if err != nil {
		s.logger.Error("Redis操作异常", "error", err)
		return err
	}

	s.logger.Info("上传帖子信息成功", "msg_id", msgId)

	return nil
}
