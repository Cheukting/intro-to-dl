#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import shutil
import tqdm
import requests
import time
from functools import wraps
import traceback
tqdm.monitor_interval = 0  # workaround for https://github.com/tqdm/tqdm/issues/481


# https://www.saltycrane.com/blog/2009/11/trying-out-retry-decorator-python/
def retry(ExceptionToCheck, tries=4, delay=3, backoff=2):
    def deco_retry(f):

        @wraps(f)
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                except KeyboardInterrupt as e:
                    raise e
                except ExceptionToCheck as e:
                    print("%s, retrying in %d seconds..." % (str(e), mdelay))
                    traceback.print_exc()
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return f(*args, **kwargs)

        return f_retry  # true decorator

    return deco_retry


@retry(Exception)
def download_file(url, file_path):
    r = requests.get(url, stream=True)
    total_size = int(r.headers.get('content-length'))
    bar = tqdm.tqdm_notebook(total=total_size, unit='B', unit_scale=True)
    bar.set_description(os.path.split(file_path)[-1])
    incomplete_download = False
    try:
        with open(file_path, 'wb', buffering=16 * 1024 * 1024) as f:
            for chunk in r.iter_content(1 * 1024 * 1024):
                f.write(chunk)
                bar.update(len(chunk))
    except Exception as e:
        raise e
    finally:
        bar.close()
        if os.path.exists(file_path) and os.path.getsize(file_path) < total_size:
            incomplete_download = True
            os.remove(file_path)
    if incomplete_download:
        raise Exception("Incomplete download")


def download_from_github(version, fn, target_dir):
    url = "https://github.com/hse-aml/intro-to-dl/releases/download/{0}/{1}".format(version, fn)
    file_path = os.path.join(target_dir, fn)
    download_file(url, file_path)


def sequential_downloader(version, fns, target_dir):
    os.makedirs(target_dir, exist_ok=True)
    for fn in fns:
        download_from_github(version, fn, target_dir)


def link_all_files_from_dir(src_dir, dst_dir):
    os.makedirs(dst_dir, exist_ok=True)
    if not os.path.exists(src_dir):
        # Coursera "readonly/readonly" bug workaround
        src_dir = src_dir.replace("readonly", "readonly/readonly")
    for fn in os.listdir(src_dir):
        src_file = os.path.join(src_dir, fn)
        dst_file = os.path.join(dst_dir, fn)
        if os.name == "nt":
            shutil.copyfile(src_file, dst_file)
        else:
            if os.path.islink(dst_file):
                os.remove(dst_file)
            os.symlink(os.path.abspath(src_file), dst_file)


def link_all_keras_resources():
    None


def link_week_3_resources():
    download_file("http://www.robots.ox.ac.uk/~vgg/data/flowers/102/102flowers.tgz", "./102flowers.tgz")
    download_file("http://www.robots.ox.ac.uk/~vgg/data/flowers/102/imagelabels.mat", "./imagelabels.mat")


def link_week_4_resources():
    download_file("http://www.cs.columbia.edu/CAVE/databases/pubfig/download/lfw_attributes.txt", "./lfw_attributes.txt")
    download_file("http://vis-www.cs.umass.edu/lfw/lfw-deepfunneled.tgz", "./lfw-deepfunneled.tgz")
    download_file("http://vis-www.cs.umass.edu/lfw/lfw.tgz", "./lfw.tgz")

def link_week_6_resources():
    download_file("http://msvocds.blob.core.windows.net/coco2014/train2014.zip", "./train2014.zip")
    download_file("http://msvocds.blob.core.windows.net/coco2014/val2014.zip", "./val2014.zip")
    download_file("http://msvocds.blob.core.windows.net/annotations-1-0-3/captions_train-val2014.zip", "./captions_train-val2014.zip")
