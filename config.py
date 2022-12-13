class Config:
	# ログイン情報を記載
	school_url = ""
	school_id = ""
	school_pass = ""

	# 予約情報の指定
	month = None
	day = None
	times_of_day = None # クラス番号

	# 教官の名前
	trainer = ""

	# 通知するslackのurl
	slack_url = ""

	# その他のパラメーター
	sleep_time = 10 # 予約が失敗した時の間隔 [s]
	start_reserve = 22 # 予約が始まる時刻 defaultは22:00

	chrome_driver_path = ""

