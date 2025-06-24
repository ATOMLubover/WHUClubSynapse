package logger

import (
	"log/slog"
	"os"
)

func CreateLogger(opts *slog.HandlerOptions) *slog.Logger {
	if opts != nil {
		return slog.New(slog.NewTextHandler(os.Stdout, opts))
	}

	opts = &slog.HandlerOptions{
		Level: slog.LevelInfo,
		ReplaceAttr: func(groups []string, a slog.Attr) slog.Attr {
			if a.Key == slog.TimeKey {
				t := a.Value.Time()
				return slog.String(slog.TimeKey, t.Format("2006-01-02 15:04:05"))
			}
			return a
		},
	}

	return slog.New(slog.NewTextHandler(os.Stdout, opts))
}
