package grpcimpl

import (
	"context"
	"fmt"
	"log/slog"
	"strconv"
	"time"
	"whuclubsynapse-server/internal/auth_server/authconfig"
	"whuclubsynapse-server/internal/auth_server/grpcimpl/mailvrf"

	grpcpool "github.com/processout/grpc-go-pool"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
)

type MailvrfClientService interface {
	RequestVerify(email string) error
}

type sMailvrfClientService struct {
	pool   *grpcpool.Pool
	logger *slog.Logger
}

func NewMailvrfClientService(
	cfg *authconfig.Config,
	logger *slog.Logger,
) MailvrfClientService {
	addr := cfg.Grpc.Host + ":" + strconv.FormatUint(uint64(cfg.Grpc.Port), 10)
	cred := grpc.WithTransportCredentials(insecure.NewCredentials())

	pool, err := grpcpool.New(
		func() (*grpc.ClientConn, error) {
			return grpc.NewClient(addr, cred)
		},
		cfg.Grpc.MinConn,
		cfg.Grpc.MaxConn,
		time.Second*30,
	)
	if err != nil {
		panic(err)
	}

	return &sMailvrfClientService{
		pool:   pool,
		logger: logger,
	}
}

func (s *sMailvrfClientService) RequestVerify(email string) error {
	ctx, cancel := context.WithTimeout(context.Background(), 3*time.Second)
	defer cancel()

	conn, err := s.pool.Get(ctx)
	if err != nil {
		return err
	}
	defer conn.Close()

	client := mailvrf.NewVerificationServiceClient(conn.ClientConn)

	res, err := client.GetVerifyCode(ctx, &mailvrf.VerificationRequest{Email: email})
	if err != nil {
		slog.Error("gRPC邮件验证服务异常", "error", err)
		return fmt.Errorf("gRPC邮件验证服务异常：%w", err)
	}
	if res.Error != 0 {
		slog.Error(
			"邮件验证服务器错误",
			"code", res.Error,
		)
		return fmt.Errorf("邮件验证服务错误码：%d", res.Error)
	}

	return nil
}
