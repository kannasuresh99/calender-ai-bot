from couchbase.cluster import Cluster
from couchbase.options import ClusterOptions
from couchbase.auth import PasswordAuthenticator
from config import COUCHBASE_URL, COUCHBASE_USERNAME, COUCHBASE_PASSWORD, COUCHBASE_BUCKET_NAME

cluster = None
bucket = None

async def init_couchbase():
    global cluster, bucket
    auth = PasswordAuthenticator(COUCHBASE_USERNAME, COUCHBASE_PASSWORD)
    cluster = Cluster(COUCHBASE_URL, ClusterOptions(auth))
    bucket = cluster.bucket(COUCHBASE_BUCKET_NAME)
    await bucket.on_connect()

def get_bucket():
    return bucket