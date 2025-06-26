package redisimpl

import (
	"context"
	"log/slog"
	"strconv"
	"time"
	"whuclubsynapse-server/internal/base_server/baseconfig"
	"whuclubsynapse-server/internal/shared/rediscli"

	"github.com/redis/go-redis/v9"
)

const (
	kVrfCodePrefix = "vrfcode_"
)

type RedisClientService interface {
	CheckVrfcodeExisting(email string) bool
	ValidateRegVrfcode(email, vrfcode string) bool
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
	ctx, cancel := context.WithTimeout(context.Background(), 3*time.Second)
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
	ctx, cancel := context.WithTimeout(context.Background(), 3*time.Second)
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
