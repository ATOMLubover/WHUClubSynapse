package main

import (
	"log/slog"
	"strings"
	"time"

	"whuclubsynapse-server/internal/base_server/baseconfig"
	"whuclubsynapse-server/internal/base_server/grpcimpl"
	"whuclubsynapse-server/internal/base_server/handler"
	"whuclubsynapse-server/internal/base_server/model"
	"whuclubsynapse-server/internal/base_server/redisimpl"
	"whuclubsynapse-server/internal/base_server/repo"
	"whuclubsynapse-server/internal/base_server/service"
	"whuclubsynapse-server/internal/shared/config"
	"whuclubsynapse-server/internal/shared/dbstruct"
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

	rootApp := mvc.New(app.Party("/"))

	config := LoadConfig("../config/basic_config.json")

	logger := CreateLogger(config)
	database := ConnectDatabase(config)
	jwtFactory := CreateJwtFactory(config, logger)

	redisService := redisimpl.NewRedisClientService(config, logger)

	userRepo := repo.CreateUserRepo(database, logger)
	categoryRepo := repo.CreateCategoryRepo(database, logger)
	clubRepo := repo.CreateClubRepo(database, logger)
	createClubAppliRepo := repo.CreateCreateClubAppliRepo(database, logger)
	joinClubAppliRepo := repo.CreateJoinClubAppliRepo(database, logger)
	clubMemberRepo := repo.CreateClubMemberRepo(database, logger)
	clubPostRepo := repo.CreateClubPostRepo(database, logger)
	updateClubInfoAppliRepo := repo.CreateUpdateClubInfoAppliRepo(database, logger)
	clubFavoriteRepo := repo.CreateClubFavoriteRepo(database, logger)

	txCoordinator := repo.NewTransactionCoordinator(database)

	userService := service.NewUserService(userRepo)
	mailvrfService := grpcimpl.NewMailvrfClientService(config, logger)
	clubService := service.NewClubService(
		userRepo,
		clubRepo,
		clubMemberRepo,
		clubPostRepo,
		createClubAppliRepo,
		joinClubAppliRepo,
		categoryRepo,
		updateClubInfoAppliRepo,
		clubFavoriteRepo,

		txCoordinator,

		logger,
	)

	rootApp.Register(
		config,

		jwtFactory,
		logger,
		database,

		// userRepo,
		// categoryRepo,
		// clubRepo,
		// createClubAppliRepo,
		// joinClubAppliRepo,
		// clubMemberRepo,
		// clubPostRepo,

		redisService,
		userService,
		mailvrfService,
		clubService,
	)

	InitAuthHandler(rootApp)
	InitApiHandler(rootApp, jwtFactory, logger)

	app.Listen(":8080")
}

func LoadConfig(relPath string) *baseconfig.Config {
	var cfg baseconfig.Config
	if err := config.LoadConfig(&cfg, relPath); err != nil {
		panic(err.Error())
	}

	return &cfg
}

func CreateLogger(cfg *baseconfig.Config) *slog.Logger {
	return logger.CreateLogger(nil)
}

func ConnectDatabase(cfg *baseconfig.Config) *gorm.DB {
	db, err := gorm.Open(
		postgres.Open(cfg.DatabaseDsn),
		&gorm.Config{},
	)
	if err != nil {
		panic(err.Error())
	}

	return db
}

func CreateJwtFactory(cfg *baseconfig.Config, lgr *slog.Logger) *jwtutil.CliamsFactory[model.UserClaims] {
	return jwtutil.NewClaimsFactory[model.UserClaims](
		time.Duration(cfg.JwtExpirationTime)*time.Hour,
		cfg.JwtSecretKey,
		lgr,
	)
}

func InitAuthHandler(parent *mvc.Application) {
	authController := parent.Party("/auth")
	authController.Handle(new(handler.AuthHandler))
}
func InitApiHandler(
	parent *mvc.Application,
	jwtFct *jwtutil.CliamsFactory[model.UserClaims],
	lgr *slog.Logger,
) {
	apiApp := parent.Party("/api")

	apiApp.Router.Use(func(ctx iris.Context) {
		authHeader := ctx.GetHeader("Authorization")
		if authHeader == "" {
			ctx.StopWithText(
				iris.StatusUnauthorized,
				"Authorization请求体缺失",
			)
			return
		}

		const kBearerPrefix = "Bearer "
		claims := strings.TrimPrefix(authHeader, kBearerPrefix)
		userClaims, err := jwtFct.ParseToken(claims)
		if err != nil {
			lgr.Info("claims反序列化错误",
				"error", err, "authHeader", authHeader,
			)

			ctx.StopWithText(
				iris.StatusUnauthorized,
				"无效的Authorization请求头",
			)
			return
		}

		ctx.Values().Set("user_claims_user_id", userClaims.UserId)
		ctx.Values().Set("user_claims_role", userClaims.Role)

		ctx.Next()
	})

	InitUserHandler(apiApp)
	InitClubHandler(apiApp, jwtFct, lgr)
}

func InitUserHandler(parent *mvc.Application) {
	userApp := parent.Party("/user")
	userApp.Handle(new(handler.UserHandler))
}

func InitClubHandler(
	parent *mvc.Application,
	jwtFct *jwtutil.CliamsFactory[model.UserClaims],
	lgr *slog.Logger,
) {
	clubApp := parent.Party("/club")
	clubApp.Handle(new(handler.ClubHandler))

	InitClubPubHandler(clubApp, jwtFct, lgr)
	InitPostHandler(clubApp)
}

func InitClubPubHandler(
	parent *mvc.Application,
	jwtFct *jwtutil.CliamsFactory[model.UserClaims],
	lgr *slog.Logger,
) {
	pubApp := parent.Party("/pub")

	pubApp.Router.Use(func(ctx iris.Context) {
		userRole := ctx.Values().GetString("user_claims_user_role")
		if userRole == "" {
			ctx.StopWithStatus(iris.StatusBadRequest)
			return
		}

		if userRole != dbstruct.ROLE_USER &&
			userRole != dbstruct.ROLE_ADMIN {
			ctx.StopWithStatus(iris.StatusForbidden)
			return
		}

		ctx.Next()
	})

	pubApp.Handle(new(handler.ClubPubHandler))
}

func InitClubAdminHandler(
	parent *mvc.Application,
	jwtFct *jwtutil.CliamsFactory[model.UserClaims],
	lgr *slog.Logger,
) {
	adminApp := parent.Party("/admin")

	adminApp.Router.Use(func(ctx iris.Context) {
		userRole := ctx.Values().GetString("user_claims_user_role")
		if userRole == "" {
			ctx.StopWithStatus(iris.StatusBadRequest)
			return
		}

		if userRole != dbstruct.ROLE_ADMIN {
			ctx.StopWithStatus(iris.StatusForbidden)
			return
		}

		ctx.Next()
	})

	adminApp.Handle(new(handler.ClubAdminHandler))
}

func InitPostHandler(parent *mvc.Application) {
	postApp := parent.Party("/post")

	postApp.Handle(new(handler.PostHandler))

	InitPostPubHandler(postApp)
}

func InitPostPubHandler(parent *mvc.Application) {
	pubApp := parent.Party("/pub")

	pubApp.Router.Use(func(ctx iris.Context) {
		userRole := ctx.Values().GetString("userRole")
		if userRole == "" {
			ctx.StopWithStatus(iris.StatusBadRequest)
			return
		}

		if userRole != dbstruct.ROLE_PUBLISHER &&
			userRole != dbstruct.ROLE_ADMIN {
			ctx.StopWithStatus(iris.StatusForbidden)
		}
	})

	pubApp.Handle(new(handler.PostPubHandler))
}
