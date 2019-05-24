from __future__ import print_function
from __future__ import division
import os
import numpy as np
import shutil
import sys
from nvidia.dali.pipeline import Pipeline
import nvidia.dali.ops as ops
import nvidia.dali.types as types
from random import shuffle

batch_size = 1
sequence_length = 10
dali_extra_path = os.environ['DALI_EXTRA_PATH']
image_dir=dali_extra_path + "/db/optical_flow/slow_preset/"
data_dir=image_dir + "/data"
if not os.path.exists(data_dir):
    os.makedirs(data_dir)
    os.makedirs(data_dir+"/0")
    

def copy_image(source,target):
    try:
       shutil.copy(source, target)
    except IOError as e:
       print("Unable to copy file. %s" % e)
    except:
       print("Unexpected error:", sys.exc_info())
       
copy_image(image_dir + "/frame_input.png", data_dir+"/0/0001.png")
copy_image(image_dir + "/frame_reference.png", data_dir+"/0/0002.png")

class OFPipeline(Pipeline):
    def __init__(self, batch_size, num_threads, device_id):
        super(OFPipeline, self).__init__(batch_size, num_threads, device_id, seed=16)
        self.input = ops.SequenceReader(file_root=image_dir+"data", sequence_length=2)
        self.of_op = ops.OpticalFlow(device="gpu", output_format=4)
    def define_graph(self):
        seq = self.input(name="Reader")
        of = self.of_op(seq.gpu())
        return of,seq.gpu()


pipe = OFPipeline(batch_size=batch_size, num_threads=1, device_id=0)
pipe.build()
pipe_out = pipe.run()
frames = pipe_out[0].as_cpu().as_array()
print(frames.shape)
np.savetxt("array.txt", frames.flatten(), fmt="%s")
myarray=np.loadtxt(image_dir+'decoded_flow_vector.dat')
assert (0.9 < np.mean(np.abs(frames[0][0].flatten()-myarray)))
