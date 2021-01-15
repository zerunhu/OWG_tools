# -*- coding:utf-8 -*-
from flask import Flask, request
import json,os,datetime,time,hashlib,re,requests,logging
import boto3
import hmac
import base64
import urllib.parse
logging.basicConfig(level=logging.INFO,format="%(asctime)s %(levelname)s %(message)s",
                    datefmt = '%Y-%m-%d  %H:%M:%S %a'    #注意月份和天数不要搞乱了，这里的格式化符与time模块相同
                    )
app1 = Flask(__name__)

def send_data_dingtalk(server_id,realstate,update_files,noupdate_files):
	##generate sign
	secret = os.environ.get('SECRET')
	access_token = os.environ.get('ACCESS_TOKEN')
	timestamp = str(round(time.time() * 1000))
	secret_enc = secret.encode('utf-8')
	string_to_sign = '{}\n{}'.format(timestamp, secret)
	string_to_sign_enc = string_to_sign.encode('utf-8')
	hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
	sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))

	url = "https://oapi.dingtalk.com/robot/send?access_token={}&timestamp={}&sign={}".format(access_token,timestamp,sign)
	header = {
		"Content-Type": "application/json",
		"charset": "utf-8"
	}
	data = {
		"msgtype": "text",
		"text": {
			"content": "serverList实际状态发生更新,将重新上传新的serverList,请检查确认, server_id:{}, realstate:{}, \
			{}将被更新,{}因为serverId不存在或者realstate没有发生改变不更新, @13142300419".format(server_id,realstate,update_files,noupdate_files)
		},
		"at": {
			"atMobiles": [
				"13142300419"
			],
			# "isAtAll":False   # 在顶顶群里@人
		}
	}
	sendData = json.dumps(data)
	res = requests.post(url, data=sendData, headers=header)
	return res.text

# def list_invalidations(DistributionId="E25WKP9A3QJD99"):
# 	session = boto3.Session(profile_name="prod")
# 	client = session.client("cloudfront")
# 	try:
# 		api_response = client.list_invalidations(DistributionId=DistributionId)
# 		invalidations = api_response.get("InvalidationList").get("Items")
# 		for invalidation in invalidations:
# 			invalidation_id = invalidation.get("Id")
# 			file_path = get_invalidations_file_path(invalidation_id)
# 			if file_path == 1:
# 				continue
# 			else:
# 				return file_path
# 		logging.info("Calling awsApi->list_invalidations: success get last invalidation: {}".format(file_path))
# 	except Exception as e:
# 		logging.info("Exception when calling awsApi->list_invalidations, reason: {}".format(e))
# 		return False
#
# def get_invalidations_file_path(invalidation_id,DistributionId="E25WKP9A3QJD99"):
# 	session = boto3.Session(profile_name="prod")
# 	client = session.client("cloudfront")
# 	try:
# 		api_response = client.get_invalidation(Id=invalidation_id,DistributionId=DistributionId)
# 		file_path = api_response.get("Invalidation").get("InvalidationBatch").get("Paths").get("Items")[0]
# 		file_path = file_path.split("/")[-1]
# 		#firestrike0.10.8  \D非数字 \d数字
# 		if not re.match("serverlist\d+\.\d+\.\d+",file_path):
# 		# if not re.match("\D+_\D+",file_path):
# 			return 1
# 		logging.info("Calling awsApi->get_invalidations: success get file_path, response: {}".format(api_response))
# 		return file_path
# 	except Exception as e:
# 		logging.info("Calling awsApi->get_invalidations: failed get file_path, reason: {}".format(e))
# 		return False

def get_last_file(bucket_name="serverpub"):
	session = boto3.Session(profile_name="prod")
	client = session.client("s3")
	try:
		files = client.list_objects(Bucket=bucket_name,Prefix='serverlist').get("Contents")
	except Exception as e:
		logging.info("Exception when calling awsApi->get_lasted_file, reason: {}".format(e))
		return False
	version_dict = {}
	for file in files:
		num = file.get("Key").split("serverlist")[-1]
		if re.match("\d+",num):
			version_dict[num] = int("".join(num.split(".")))
	nums = list(version_dict.values())
	nums.sort()
	versions = [key for key, value in version_dict.items() if value == nums[-1] or value == nums[-2] or value == nums[-3]]
	last_files = ["serverlist"+version for version in versions]
	logging.info("Calling awsApi->get_last_file,success get last_files: {}".format(last_files))
	return last_files


def download_file(dir_path, file_name, bucket_name="serverpub"):
	session = boto3.Session(profile_name="prod")
	client = session.client("s3")
	try:
		file_path = "{}/{}".format(dir_path,file_name)
		client.download_file(bucket_name, file_name, file_path)
		logging.info("Calling awsApi->download_file: success download file: {} from bucket: {}-> {}".format(file_name, bucket_name, file_path))
		return file_path
	except Exception as e:
		logging.info("Exception when calling awsApi->download_file, reason: {}".format(e))
		return False

def update_file(file_path,server_id,realstate):
	with open(file_path,"rb") as f:
		is_update = False
		params = json.load(f)
		for param in params:
			if param.get("id") == server_id:
				logging.info(param["realstate"])
				if param["realstate"] != realstate:
					param["realstate"] = realstate
					is_update = True
					break
				break
		data = params
	if not is_update:
		return is_update
	with open(file_path,"w") as f:
		json.dump(data, f, indent=4)
	return is_update

def upload_file(file_path, file_name, bucket_name="serverpub"):
	session = boto3.Session(profile_name="prod")
	client = session.client("s3")
	try:
		client.upload_file(file_path, bucket_name, file_name)
		logging.info("Calling awsApi->upload_file: success upload file: {} to bucket: {}-> {}".format(file_path, bucket_name,file_name))
		return file_name
	except Exception as e:
		logging.info("Exception when calling awsApi->upload_file, reason: {}".format(e))
		return False

def create_invalidation(file_name, DistributionId="E25WKP9A3QJD99"):
	session = boto3.Session(profile_name="prod")
	client = session.client("cloudfront")
	InvalidationBatch = {
		'Paths': {
			'Quantity': 1,
			'Items': [
				'/{}'.format(file_name),
			]
		},
		'CallerReference': str(time.time())
	}
	try:
		api_response = client.create_invalidation(DistributionId=DistributionId, InvalidationBatch=InvalidationBatch)
		invalidatoin_id = api_response.get("Invalidation").get("Id")
		logging.info("Calling awsApi->create_invalidation: success create invalidation: {}".format(invalidatoin_id))
	except Exception as e:
		logging.info("Exception when calling awsApi->create_invalidation, reason: {}".format(e))
		return False
	return invalidatoin_id

@app1.route('/serverList', methods=['POST'])
def updateServerlist():
	data = json.loads(request.data)
	server_id = data.get("server_id")
	realstate = data.get("realstate")
	sign = data.get("sign")
	httpsecretkey = os.environ.get('HTTPSECRETKEY')
	if not isinstance(sign, str):
		msg = {"code": 400, "status": "Failed", "message": "parame sign error"}
		logging.info(msg)
		return msg
	if not isinstance(server_id,int):
		msg = {"code":400, "status": "Failed", "message": "parame server_id error"}
		logging.info(msg)
		return msg
	if not isinstance(realstate,int):
		msg = {"code": 400, "status": "Failed", "message": "parame realstate error"}
		logging.info(msg)
		return msg
	s = "SERVER_ID{}REALSTATE{}HTTPSECRETKEY{}".format(server_id,realstate,httpsecretkey)
	server_sign = hashlib.md5(s.encode("utf-8")).hexdigest()
	if sign != server_sign:
		msg = {"code": 400, "status": "Failed", "message": "Parameter sign verification failed"}
		logging.info(msg)
		return msg


	files_path = get_last_file()
	if not files_path:
		msg = {"code": 400, "status": "Failed", "message": "get last_files path error"}
		logging.info(msg)
		return msg
	files_hostpath = {}  #{"hostpath":is_update}
	#是否需要更新
	update_mark = False
	##以时间为名创建一个目录存储下载的serverlist
	stime = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
	dir_path = "/tmp/{}".format(stime)
	os.mkdir(dir_path)
	for file_path in files_path:
		##下载serverlist
		host_path = download_file(dir_path,file_path)
		if not host_path: #返回false的话就是下载失败了
			msg = {"code": 400, "status": "Failed", "message": "download s3 file error"}
			logging.info(msg)
			return msg
		#更新下载的serverlist
		is_update = update_file(host_path,server_id,realstate)
		if is_update == True:  #如果有更新 就修改update_mark的值
			update_mark = True
		files_hostpath[host_path]=is_update
	if not update_mark:  #update_mark值没有修改，说明所有文件都没更新
		msg = {"code": 200, "status": "Success", "message": "success download file, but all serverlist not been modified or one serverlist server_id not exist, serverlist: {}, server_id: {}, realstate: {}".format(files_path,server_id, realstate)}
		logging.info(msg)
		return msg
	update_host_files = []
	noupdate_host_files = []
	for file in files_hostpath:
		if files_hostpath[file]:
			update_host_files.append(file)
		else:
			noupdate_host_files.append(file)
	update_files = [file.split("/")[-1] for file in update_host_files]
	noupdate_files = [file.split("/")[-1] for file in noupdate_host_files]
	send_data_dingtalk(server_id,realstate,update_files,noupdate_files)
	for file in update_host_files:
		file_name = upload_file(file,file.split("/")[-1])
		if not file_name:
			msg = {"code": 400, "status": "Failed", "message": "upload s3 file error"}
			logging.info(msg)
			return msg
		invalidation_id = create_invalidation(file_name)
		if not invalidation_id:
			msg = {"code": 400, "status": "Failed", "message": "create invalidation error"}
			logging.info(msg)
			return msg
	msg = {"code": 200, "status": "Success", "message": "success update serverlists: {}".format(update_files)}
	logging.info(msg)
	return msg

if __name__ == "__main__":
	app1.run(debug=False,host='0.0.0.0',port=12345)

