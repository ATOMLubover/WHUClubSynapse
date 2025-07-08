package rediscli

import (
	"context"
	"time"

	"github.com/redis/go-redis/v9"
)

type RedisClient struct {
	rdb *redis.Client
}

func NewRedisClient(
	addr string,
	password string,
	maxConn int,
	minIdle int,
	MaxRetries int,
) *RedisClient {
	rdb := redis.NewClient(&redis.Options{
		Addr:         addr,
		Password:     password,
		DB:           0,
		PoolSize:     maxConn,
		MinIdleConns: minIdle,
		MaxRetries:   MaxRetries,
		PoolTimeout:  0,
	})

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()
	_, err := rdb.Ping(ctx).Result()
	if err != nil {
		panic(err)
	}

	return &RedisClient{
		rdb: rdb,
	}
}

func (r *RedisClient) Inst() *redis.Client {
	return r.rdb
}
