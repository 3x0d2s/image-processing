package config

import (
	"os"
)

type Config struct {
	DbSaverPgDsn             string
	RedisDsn                 string
	RedisStreamToDbSaverName string
	RedisDbSaverGroupKey     string
	RedisDbSaverConsumerName string
	MediaRoot                string
}

// New returns a new Config struct
func New() *Config {
	return &Config{
		DbSaverPgDsn:             getEnv("DB_SAVER_PG_DSN", ""),
		RedisDsn:                 getEnv("REDIS_DSN", ""),
		RedisStreamToDbSaverName: getEnv("REDIS_STREAM_TO_DB_SAVER_NAME", ""),
		RedisDbSaverGroupKey:     getEnv("REDIS_DB_SAVER_GROUP_KEY", ""),
		RedisDbSaverConsumerName: getEnv("REDIS_DB_SAVER_CONSUMER_NAME", ""),
		MediaRoot:                getEnv("MEDIA_ROOT", ""),
	}
}

// getEnv is simple helper function to read an environment or return a default value
func getEnv(key string, defaultVal string) string {
	if value, exists := os.LookupEnv(key); exists {
		return value
	}
	return defaultVal
}
