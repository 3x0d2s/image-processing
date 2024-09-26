package main

import (
	"context"
	"database/sql"
	"db_saver/config"
	"errors"
	"fmt"
	"github.com/joho/godotenv"
	_ "github.com/lib/pq"
	"github.com/redis/go-redis/v9"
	"log"
	"os"
	"strconv"
	"time"
)

var (
	ctx     = context.Background()
	conf    *config.Config
	rdb     *redis.Client
	db      *sql.DB
	logFile *os.File
)

// init is invoked before main()
func init() {
	logFile, err := os.OpenFile("logs/log.log", os.O_RDWR|os.O_CREATE|os.O_APPEND, 0644)
	if err != nil {
		log.Fatalf("error opening file: %v", err)
	}
	log.SetFlags(log.Lshortfile | log.LstdFlags)
	log.SetOutput(logFile)

	// loads values from .env into the system
	if err := godotenv.Load(); err != nil {
		log.Print("No .env file found")
	}
	conf = config.New()

	opt, err := redis.ParseURL(conf.RedisDsn)
	if err != nil {
		log.Fatal(err)
	}
	rdb = redis.NewClient(opt)
	err = rdb.XGroupCreateMkStream(ctx, conf.RedisStreamToDbSaverName, conf.RedisDbSaverGroupKey, "0").Err()
	if err != nil {
		log.Println(err.Error())
	}

	db, err = sql.Open("postgres", conf.DbSaverPgDsn)
	if err != nil {
		log.Fatal(err)
	}
}

func main() {
	processPendingMessages()
	processNewMessages()
	//
	rdb.Close()
	db.Close()
	logFile.Close()
}

// processPendingMessages processes "pending" messages, which the script has
// already received before, but has not executed msg.ack()
func processPendingMessages() {
	for {
		result, err := rdb.XReadGroup(ctx, &redis.XReadGroupArgs{
			Streams:  []string{conf.RedisStreamToDbSaverName, "0"},
			Group:    conf.RedisDbSaverGroupKey,
			Consumer: conf.RedisDbSaverConsumerName,
			Count:    5,
		}).Result()
		if err != nil {
			if !errors.Is(err, redis.Nil) {
				log.Fatal("failed to get stream records", err)
			}
		}
		s := result[0]
		if len(s.Messages) == 0 {
			return
		}
		for _, message := range s.Messages {
			val, err := rdb.Do(
				ctx,
				"XPENDING",
				conf.RedisStreamToDbSaverName,
				conf.RedisDbSaverGroupKey,
				message.ID,
				message.ID,
				1).Slice()
			if err != nil {
				log.Fatal(err)
			}
			msgData := val[0].([]interface{})
			timesDelivered := msgData[3].(int64)
			if timesDelivered >= 3 {
				log.Println("The script cannot process message")
			} else {
				saveImageToDb(message.Values)
			}
			ackAndDelMsg(message.ID)
		}
	}
}

func processNewMessages() {
	for {
		result, err := rdb.XReadGroup(ctx, &redis.XReadGroupArgs{
			Streams:  []string{conf.RedisStreamToDbSaverName, ">"},
			Group:    conf.RedisDbSaverGroupKey,
			Consumer: conf.RedisDbSaverConsumerName,
			Count:    1,
			Block:    0,
		}).Result()
		if err != nil {
			if !errors.Is(err, redis.Nil) {
				log.Fatal("failed to get stream records", err)
			}
		}
		s := result[0]
		for _, message := range s.Messages {
			saveImageToDb(message.Values)
			//
			ackAndDelMsg(message.ID)
		}
	}
}

func saveImageToDb(msgData map[string]interface{}) {
	timestampFloat, err := strconv.ParseFloat(msgData["dt"].(string), 64)
	if err != nil {
		panic(err)
	}
	seconds := int64(timestampFloat)
	nanoseconds := int64((timestampFloat - float64(seconds)) * 1e9)
	t := time.Unix(seconds, nanoseconds)
	tStr := t.Format("2006-01-02_15_04_05.0000")
	imgFileName := fmt.Sprintf("image_%s.jpg", tStr)
	imgPath := fmt.Sprintf("%s/%s", conf.MediaRoot, imgFileName)
	//
	f, err := os.Create(imgPath)
	if err != nil {
		log.Fatal(err)
	}
	imgByteArray := []byte(msgData["image"].(string))
	_, err = f.Write(imgByteArray)
	if err != nil {
		log.Fatal(err)
	}
	log.Println("The image was saved successfully")
	err = f.Close()
	if err != nil {
		log.Fatal(err)
	}
	//
	_, err = db.Query(
		`INSERT INTO "Image" (dt, description, file_path) VALUES ($1, $2, $3)`,
		t,
		msgData["description"].(string),
		imgFileName,
	)
	if err != nil {
		log.Fatal("Data saving error: ", err)
	}
	log.Println("An entry with this image has been added to the database")
}

func ackAndDelMsg(messageId string) {
	err := rdb.XAck(ctx,
		conf.RedisStreamToDbSaverName,
		conf.RedisDbSaverGroupKey,
		messageId).Err()
	if err != nil {
		log.Fatal("acknowledgment failed for", messageId, err)
	}
	log.Println("acknowledged message", messageId)
	err = rdb.XDel(ctx, conf.RedisStreamToDbSaverName, messageId).Err()
	if err != nil {
		log.Fatal("delete failed for", messageId, err)
	}
	log.Println("delete message", messageId)
}
