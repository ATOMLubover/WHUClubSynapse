package main

import (
	"log/slog"
	"time"

	"whuclubsynapse-server/internal/auth_server/authconfig"
	"whuclubsynapse-server/internal/auth_server/grpcimpl"
	"whuclubsynapse-server/internal/auth_server/handler"
	"whuclubsynapse-server/internal/auth_server/model"
	"whuclubsynapse-server/internal/auth_server/redisimpl"
	"whuclubsynapse-server/internal/auth_server/repo"
	"whuclubsynapse-server/internal/auth_server/service"
	"whuclubsynapse-server/internal/shared/config"
	"whuclubsynapse-server/internal/shared/jwtutil"
	"whuclubsynapse-server/internal/shared/logger"

	"github.com/kataras/iris/v12"
	"github.com/kataras/iris/v12/mvc"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

func main() {
	app := iris.Default()
	app.Logger().SetLevel("debug")

	globalController := mvc.New(app.Party("/"))

	config := LoadConfig("../../config/auth_config.json")

	logger := CreateLogger(config)
	database := ConnectDatabase(config)
	jwtFactory := CreateJwtFactory(config, logger)

	redisService := redisimpl.NewRedisClientService(config, logger)

	userRepo := repo.CreateUserRepo(database, logger)

	userService := service.NewUserService(userRepo)
	mailvrfService := grpcimpl.NewMailvrfClientService(config, logger)

	globalController.Register(
		config,

		jwtFactory,
		logger,
		database,

		userRepo,

		redisService,
		userService,
		mailvrfService,
	)

	{
		authController := globalController.Party("/user")
		authController.Handle(new(handler.UserHandler))
	}

	app.Listen(":8080")
}

func LoadConfig(relPath string) *authconfig.Config {
	var cfg authconfig.Config
	if err := config.LoadConfig(&cfg, relPath); err != nil {
		panic(err.Error())
	}

	return &cfg
}

func CreateLogger(cfg *authconfig.Config) *slog.Logger {
	return logger.CreateLogger(nil)
}

func ConnectDatabase(cfg *authconfig.Config) *gorm.DB {
	db, err := gorm.Open(
		postgres.Open(cfg.DatabaseDsn),
		&gorm.Config{},
	)
	if err != nil {
		panic(err.Error())
	}

	return db
}

func CreateJwtFactory(cfg *authconfig.Config, lgr *slog.Logger) *jwtutil.CliamsFactory[model.UserClaims] {
	return jwtutil.NewClaimsFactory[model.UserClaims](
		time.Duration(cfg.JwtExpirationTime)*time.Hour,
		cfg.JwtSecretKey,
		lgr,
	)
}
