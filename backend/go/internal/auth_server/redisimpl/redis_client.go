package redisimpl

import (
	"context"
	"log/slog"
	"strconv"
	"time"
	"whuclubsynapse-server/internal/auth_server/authconfig"
	"whuclubsynapse-server/internal/shared/rediscli"

	"github.com/redis/go-redis/v9"
)

type RedisClientService interface {
	ValidateRegVrfcode(email, vrfcode string) bool
}

type sRedisClientService struct {
	client *rediscli.RedisClient

	logger *slog.Logger
}

func NewRedisClientService(
	cfg *authconfig.Config,
	logger *slog.Logger,
) RedisClientService {
	client := rediscli.NewRedisClient(
		cfg.Redis.Host+":"+strconv.FormatUint(uint64(cfg.Redis.Port), 10),
		cfg.Redis.Password,
		cfg.Redis.MaxConn,
		cfg.Redis.MinIdle,
		cfg.Redis.MaxRetries,
	)
	return &sRedisClientService{
		client: client,
		logger: logger,
	}
}

func (s *sRedisClientService) ValidateRegVrfcode(email, vrfcode string) bool {
	ctx, cancel := context.WithTimeout(context.Background(), 3*time.Second)
	defer cancel()

	const kVrfCodePrefix = "vrfcode_"
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
