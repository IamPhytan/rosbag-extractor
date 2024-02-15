import os
import pandas as pd
from pathlib import Path
from tqdm import tqdm
from rosbags.highlevel import AnyReader
import numpy as np

DATA_TYPES = {
    1 : np.int8,
    2 : np.uint8,
    3 : np.int16,
    4 : np.uint16,
    5 : np.int32,
    6 : np.uint32,
    7 : np.float32,
    8 : np.float64
}

def extract_point_clouds_from_rosbag(bag_file, topic_name, output_folder):
    os.makedirs(output_folder)
    with AnyReader([Path(bag_file)]) as reader:
        print(f"Extracting point clouds from topic \"{topic_name}\" to folder \"{output_folder.split('/')[-1]}\"")
        connections = [x for x in reader.connections if x.topic == topic_name]
        for connection, _, rawdata in tqdm(reader.messages(connections=connections)):
            msg = reader.deserialize(rawdata, connection.msgtype)
            timestamp = msg.header.stamp.sec * 1e9 + msg.header.stamp.nanosec
            df = pd.DataFrame()
            data = np.frombuffer(msg.data, dtype=np.uint8).reshape(-1, msg.point_step)
            for field in msg.fields:
                print(field.name)
                type = DATA_TYPES[field.datatype]
                n_bytes = np.dtype(type).itemsize
                df[field.name] = data[:, field.offset : field.offset + n_bytes].view(dtype=type).flatten()
            df.to_csv(os.path.join(output_folder, f"{int(timestamp):d}.csv"), index=False)
    print(f"Done ! Exported point clouds to {output_folder}")