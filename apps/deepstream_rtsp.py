#!/usr/bin/env python3
import numpy as np
import pyds
from common.FPS import GETFPS
from common.bus_call import bus_call
from common.is_aarch_64 import is_aarch64
import math
import time
from ctypes import *
from gi.repository import GObject, Gst
import gi
import sys
sys.path.append('../')
gi.require_version('Gst', '1.0')

fps_streams = {}
perf_data = None
MAX_DISPLAY_LEN = 64
MUXER_OUTPUT_WIDTH = 640
MUXER_OUTPUT_HEIGHT = 480
MUXER_BATCH_TIMEOUT_USEC = 4000000
TILED_OUTPUT_WIDTH = 640
TILED_OUTPUT_HEIGHT = 480
GST_CAPS_FEATURES_NVMM = "memory:NVMM"
OSD_PROCESS_MODE = 0
OSD_DISPLAY_TEXT = 1
PGIE_CLASS_ID_TOOTHBRUSH = 80
PGIE_CLASS_ID_HAIR_DRYER = 79
PGIE_CLASS_ID_TEDDY_BEAR = 78
PGIE_CLASS_ID_SCISSORS = 77
PGIE_CLASS_ID_VASE = 76
PGIE_CLASS_ID_CLOCK = 75
PGIE_CLASS_ID_BOOK = 74
PGIE_CLASS_ID_REFRIGERATOR = 73
PGIE_CLASS_ID_SINK = 72
PGIE_CLASS_ID_TOASTER = 71
PGIE_CLASS_ID_OVEN = 70
PGIE_CLASS_ID_MICROWAVE = 69
PGIE_CLASS_ID_CELL_PHONE = 68
PGIE_CLASS_ID_KEYBOARD = 67
PGIE_CLASS_ID_REMOTE = 66
PGIE_CLASS_ID_MOUSE = 65
PGIE_CLASS_ID_LAPTOP = 64
PGIE_CLASS_ID_TVMONITOR = 63
PGIE_CLASS_ID_TOILET = 62
PGIE_CLASS_ID_DININGTABLE= 61
PGIE_CLASS_ID_BED = 60
PGIE_CLASS_ID_POTTEDPLANT = 59
PGIE_CLASS_ID_SOFA = 58
PGIE_CLASS_ID_CHAIR = 57
PGIE_CLASS_ID_CAKE = 56
PGIE_CLASS_ID_DONUT = 55
PGIE_CLASS_ID_PIZZA = 54
PGIE_CLASS_ID_HOT_DOG = 53
PGIE_CLASS_ID_CARROT = 52
PGIE_CLASS_ID_BROCCOLI = 51
PGIE_CLASS_ID_ORANGE = 50
PGIE_CLASS_ID_SANDWICH = 49
PGIE_CLASS_ID_APPLE = 48
PGIE_CLASS_ID_BANANA = 47
PGIE_CLASS_ID_BOWL = 46
PGIE_CLASS_ID_SPOON = 45
PGIE_CLASS_ID_KNIFE = 44
PGIE_CLASS_ID_FORK = 43
PGIE_CLASS_ID_CUP = 42
PGIE_CLASS_ID_WINE_GLASS = 41
PGIE_CLASS_ID_BOTTLE = 40
PGIE_CLASS_ID_TENNIS_RACKET = 39
PGIE_CLASS_ID_SURFBOARD = 38
PGIE_CLASS_ID_SKATEBOARD = 37
PGIE_CLASS_ID_BASEBALL_GLOVE = 36
PGIE_CLASS_ID_BASEBALL_BAT = 35
PGIE_CLASS_ID_KITE = 34
PGIE_CLASS_ID_SPORTS_BALL = 33
PGIE_CLASS_ID_SNOWBOARD = 32
PGIE_CLASS_ID_SKIS = 31
PGIE_CLASS_ID_FRISBEE = 30
PGIE_CLASS_ID_SUITCASE = 29
PGIE_CLASS_ID_TIE = 28
PGIE_CLASS_ID_HANDBAG = 27
PGIE_CLASS_ID_UMBRELLA = 26
PGIE_CLASS_ID_BACKPACK = 25
PGIE_CLASS_ID_UMBRELLA = 24
PGIE_CLASS_ID_GIRAFFE = 23
PGIE_CLASS_ID_ZEBRA = 22
PGIE_CLASS_ID_BEAR = 21
PGIE_CLASS_ID_ELEPHANT = 20
PGIE_CLASS_ID_COW = 19
PGIE_CLASS_ID_SHEEP = 18
PGIE_CLASS_ID_HORSE = 17
PGIE_CLASS_ID_DOG = 16
PGIE_CLASS_ID_CAT = 15
PGIE_CLASS_ID_BIRD = 14
PGIE_CLASS_ID_BENCH = 13
PGIE_CLASS_ID_PARKING_METER = 12
PGIE_CLASS_ID_STOP_SIGN = 11
PGIE_CLASS_ID_FIRE_HYDRANT = 10
PGIE_CLASS_ID_TRAFFIC_LIGHT = 9
PGIE_CLASS_ID_BOAT = 8
PGIE_CLASS_ID_TRUCK = 7
PGIE_CLASS_ID_TRAIN = 6
PGIE_CLASS_ID_BUS = 5
PGIE_CLASS_ID_AEROPLANE = 4
PGIE_CLASS_ID_MOTORBIKE = 3
PGIE_CLASS_ID_VEHICLE = 2
PGIE_CLASS_ID_BICYCLE = 1
PGIE_CLASS_ID_PERSON = 0



start_time = time.time()
frame_count = 0
fps_streams = {}
fpsarray = []


class GETFPS:
    def __init__(self, stream_id):
        global start_time
        self.start_time = start_time
        self.is_first = True
        global frame_count
        self.frame_count = frame_count
        self.stream_id = stream_id

    def print_data(self):
        print('frame_count=', self.frame_count)
        print('start_time=', self.start_time)

    def calc_fps(self):
        end_time = time.time()
        elapsed_time = end_time - self.start_time
        current_fps = 1.0/float(elapsed_time)
        self.start_time = end_time
        return current_fps


# tiler_sink_pad_buffer_probe  will extract metadata received on tiler sink pad
# and re-size and binarize segmentation mask array to save to image
def tiler_src_pad_buffer_probe2(pad, info, u_data):
    frame_number = 0
    num_rects = 0
    gst_buffer = info.get_buffer()
    if not gst_buffer:
        print("Unable to get GstBuffer ")
        return

    # Retrieve batch metadata from the gst_buffer
    # Note that pyds.gst_buffer_get_nvds_batch_meta() expects the
    # C address of gst_buffer as input, which is obtained with hash(gst_buffer)
    batch_meta = pyds.gst_buffer_get_nvds_batch_meta(hash(gst_buffer))

    l_frame = batch_meta.frame_meta_list
    while l_frame is not None:
        try:
            # Note that l_frame.data needs a cast to pyds.NvDsFrameMeta
            # The casting is done by pyds.NvDsFrameMeta.cast()
            # The casting also keeps ownership of the underlying memory
            # in the C code, so the Python garbage collector will leave
            # it alone.
            frame_meta = pyds.NvDsFrameMeta.cast(l_frame.data)
        except StopIteration:
            break

        frame_number = frame_meta.frame_num
        l_obj = frame_meta.obj_meta_list
        num_rects = frame_meta.num_obj_meta
        is_first_obj = True
        # save_image = True
        obj_number = 0
        while l_obj is not None:
            try:
                # Casting l_obj.data to pyds.NvDsObjectMeta
                obj_meta = pyds.NvDsObjectMeta.cast(l_obj.data)
            except StopIteration:
                break
            # print("the frame number is", frame_number)
            if is_first_obj and frame_number % 30 == 0:
                is_first_obj = False
                # Retrieve rectparams for re-sizing mask to correct dims
                rectparams = obj_meta.rect_params
                maskparams = obj_meta.mask_params  # Retrieve maskparams

            try:
                l_obj = l_obj.next
                obj_number += 1
            except StopIteration:
                break

        print("Frame Number=", frame_number, "Number of Objects=", num_rects)
        try:
            l_frame = l_frame.next
        except StopIteration:
            break

    return Gst.PadProbeReturn.OK


def clip(val, low, high):
    if val < low:
        return low
    elif val > high:
        return high
    else:
        return val
    
def tiler_src_pad_buffer_probe(pad, info, u_data):
    # Drawing and postprocessing
    frame_number = 0
    num_rects = 0
    gst_buffer = info.get_buffer()
    if not gst_buffer:
        print("Unable to get GstBuffer ")
        return

    # Retrieve batch metadata from the gst_buffer
    # Note that pyds.gst_buffer_get_nvds_batch_meta() expects the
    # C address of gst_buffer as input, which is obtained with hash(gst_buffer)
    batch_meta = pyds.gst_buffer_get_nvds_batch_meta(hash(gst_buffer))
    l_frame = batch_meta.frame_meta_list
    while l_frame is not None:
        try:
            # Note that l_frame.data needs a cast to pyds.NvDsFrameMeta
            # The casting is done by pyds.NvDsFrameMeta.cast()
            # The casting also keeps ownership of the underlying memory
            # in the C code, so the Python garbage collector will leave
            # it alone.
            frame_meta = pyds.NvDsFrameMeta.cast(l_frame.data)
        except StopIteration:
            break

        # print("Frame Number is ", frame_meta.frame_num)
        # print("Source id is ", frame_meta.source_id)
        # print("Batch id is ", frame_meta.batch_id)
        # print("Source Frame Width ", frame_meta.source_frame_width)
        # print("Source Frame Height ", frame_meta.source_frame_height)
        # print("Num object meta ", frame_meta.num_obj_meta)

        frame_number = frame_meta.frame_num
        l_obj = frame_meta.obj_meta_list
        num_rects = frame_meta.num_obj_meta
        obj_counter = {
            PGIE_CLASS_ID_PERSON: 0,
            PGIE_CLASS_ID_MOUSE: 0
        }
        while l_obj is not None:
            try:
                # Casting l_obj.data to pyds.NvDsObjectMeta
                obj_meta = pyds.NvDsObjectMeta.cast(l_obj.data)
            except StopIteration:
                break
            obj_counter[obj_meta.class_id] += 1
            # obj_meta.rect_params.border_color.set(0.0, 0.0, 1.0, 0.0)
            try:
                l_obj = l_obj.next
            except StopIteration:
                break
         # Acquiring a display meta object. The memory ownership remains in
        # the C code so downstream plugins can still access it. Otherwise
        # the garbage collector will claim it when this probe function exits.
        display_meta = pyds.nvds_acquire_display_meta_from_pool(batch_meta)
        display_meta.num_labels = 2
        py_nvosd_text_params = display_meta.text_params[0]
        # Setting display text to be shown on screen
        # Note that the pyds module allocates a buffer for the string, and the
        # memory will not be claimed by the garbage collector.
        # Reading the display_text field here will return the C address of the
        # allocated string. Use pyds.get_string() to get the string content.

        fps = fps_streams["stream{0}".format(frame_meta.pad_index)].calc_fps()
        fpsarray.append(fps)
        fps = "%.1f" % (fps)
        avg = "%.1f" % (sum(fpsarray)/len(fpsarray))

        # py_nvosd_text_params.display_text = "Frame Number={} Number of Objects={} Box_count={} Pill_count={}".format(frame_number, num_rects, obj_counter[PGIE_CLASS_ID_BOX], obj_counter[PGIE_CLASS_ID_PILL])
        py_nvosd_text_params.display_text = "FPS={} Avg FPS={} Frame Number={}\nNumber of Objects={} Class1_count={} Class2_count={}".format(
            fps, avg, frame_number, num_rects, obj_counter[PGIE_CLASS_ID_PERSON], obj_counter[PGIE_CLASS_ID_MOUSE])
        # Now set the offsets where the string should appear
        py_nvosd_text_params.x_offset = 10
        py_nvosd_text_params.y_offset = 12

        # Font , font-color and font-size
        py_nvosd_text_params.font_params.font_name = "Serif"
        py_nvosd_text_params.font_params.font_size = 10
        # set(red, green, blue, alpha); set to White
        py_nvosd_text_params.font_params.font_color.set(1.0, 1.0, 1.0, 1.0)

        # Text background color
        py_nvosd_text_params.set_bg_clr = 1
        # set(red, green, blue, alpha); set to Black
        py_nvosd_text_params.text_bg_clr.set(0.0, 0.0, 0.0, 1.0)
        # Using pyds.get_string() to get display_text as string
        print(pyds.get_string(py_nvosd_text_params.display_text))
        pyds.nvds_add_display_meta_to_frame(frame_meta, display_meta)
        # fps = fps_streams["stream{0}".format(frame_meta.pad_index)].get_fps()
        # print("the number of fps is",fps)
        try:
            l_frame = l_frame.next
        except StopIteration:
            break

    return Gst.PadProbeReturn.OK


def cb_newpad(decodebin, decoder_src_pad, data):
    print("In cb_newpad\n")
    caps = decoder_src_pad.get_current_caps()
    gststruct = caps.get_structure(0)
    gstname = gststruct.get_name()
    source_bin = data
    features = caps.get_features(0)

    # Need to check if the pad created by the decodebin is for video and not
    # audio.
    print("gstname=", gstname)
    if gstname.find("video") != -1:
        # Link the decodebin pad only if decodebin has picked nvidia
        # decoder plugin nvdec_*. We do this by checking if the pad caps contain
        # NVMM memory features.
        print("features=", features)
        if features.contains("memory:NVMM"):
            # Get the source bin ghost pad
            bin_ghost_pad = source_bin.get_static_pad("src")
            if not bin_ghost_pad.set_target(decoder_src_pad):
                sys.stderr.write(
                    "Failed to link decoder src pad to source bin ghost pad\n")
        else:
            sys.stderr.write(
                " Error: Decodebin did not pick nvidia decoder plugin.\n")


def decodebin_child_added(child_proxy, Object, name, user_data):
    print("Decodebin child added:", name, "\n")
    if (name.find("decodebin") != -1):
        Object.connect("child-added", decodebin_child_added, user_data)
    # if(is_aarch64() and name.find("nvv4l2decoder") != -1):
    #     print("Seting bufapi_version\n")
    #     Object.set_property("bufapi-version",True)


def create_source_bin(index, uri):
    print("Creating source bin")

    # Create a source GstBin to abstract this bin's content from the rest of the
    # pipeline
    bin_name = "source-bin-%02d" % index
    print(bin_name)
    nbin = Gst.Bin.new(bin_name)
    if not nbin:
        sys.stderr.write(" Unable to create source bin \n")

    # Source element for reading from the uri.
    # We will use decodebin and let it figure out the container format of the
    # stream and the codec and plug the appropriate demux and decode plugins.
    uri_decode_bin = Gst.ElementFactory.make("uridecodebin", "uri-decode-bin")
    if not uri_decode_bin:
        sys.stderr.write(" Unable to create uri decode bin \n")
    # We set the input uri to the source element
    uri_decode_bin.set_property("uri", uri)
    # Connect to the "pad-added" signal of the decodebin which generates a
    # callback once a new pad for raw data has beed created by the decodebin
    uri_decode_bin.connect("pad-added", cb_newpad, nbin)
    uri_decode_bin.connect("child-added", decodebin_child_added, nbin)

    # We need to create a ghost pad for the source bin which will act as a proxy
    # for the video decoder src pad. The ghost pad will not have a target right
    # now. Once the decode bin creates the video decoder and generates the
    # cb_newpad callback, we will set the ghost pad target to the video decoder
    # src pad.
    Gst.Bin.add(nbin, uri_decode_bin)
    bin_pad = nbin.add_pad(
        Gst.GhostPad.new_no_target("src", Gst.PadDirection.SRC))
    if not bin_pad:
        sys.stderr.write(" Failed to add ghost pad in source bin \n")
        return None
    return nbin


def main(args):
    # Check input arguments
    if len(args) < 2:
        sys.stderr.write("usage: %s <uri1> [uri2] ... [uriN]\n" % args[0])
        sys.exit(1)

    for i in range(0, len(args)-1):
        fps_streams["stream{0}".format(i)] = GETFPS(i)
    number_sources = len(args)-1

    # Standard GStreamer initialization
    GObject.threads_init()
    Gst.init(None)

    # Create gstreamer elements */
    # Create Pipeline element that will form a connection of other elements
    print("Creating Pipeline \n ")
    pipeline = Gst.Pipeline()
    is_live = False

    if not pipeline:
        sys.stderr.write(" Unable to create Pipeline \n")
    print("Creating streamux \n ")

    # Create nvstreammux instance to form batches from one or more sources.
    streammux = Gst.ElementFactory.make("nvstreammux", "Stream-muxer")
    if not streammux:
        sys.stderr.write(" Unable to create NvStreamMux \n")

    pipeline.add(streammux)
    for i in range(number_sources):
        print("Creating source_bin ", i, " \n ")
        uri_name = args[i+1]
        if uri_name.find("rtsp://") == 0:
            is_live = True
        source_bin = create_source_bin(i, uri_name)
        if not source_bin:
            sys.stderr.write("Unable to create source bin \n")
        pipeline.add(source_bin)
        padname = "sink_%u" % i
        sinkpad = streammux.get_request_pad(padname)
        if not sinkpad:
            sys.stderr.write("Unable to create sink pad bin \n")
        srcpad = source_bin.get_static_pad("src")
        if not srcpad:
            sys.stderr.write("Unable to create src pad bin \n")
        srcpad.link(sinkpad)
    queue1 = Gst.ElementFactory.make("queue", "queue1")
    queue2 = Gst.ElementFactory.make("queue", "queue2")
    queue3 = Gst.ElementFactory.make("queue", "queue3")
    queue4 = Gst.ElementFactory.make("queue", "queue4")
    queue5 = Gst.ElementFactory.make("queue", "queue5")
    pipeline.add(queue1)
    pipeline.add(queue2)
    pipeline.add(queue3)
    pipeline.add(queue4)
    pipeline.add(queue5)

    print("Creating Pgie \n ")
    pgie = Gst.ElementFactory.make("nvinfer", "primary-inference")
    # pgie = Gst.ElementFactory.make("nvinferserver", "primary-inference")
    if not pgie:
        sys.stderr.write(" Unable to create pgie \n")
    tracker = Gst.ElementFactory.make("nvtracker", "tracker")
    if not tracker:
        sys.stderr.write(" Unable to create tracker \n")

    print("Creating tiler \n ")
    tiler = Gst.ElementFactory.make("nvmultistreamtiler", "nvtiler")
    if not tiler:
        sys.stderr.write(" Unable to create tiler \n")
    print("Creating nvvidconv \n ")
    nvvidconv = Gst.ElementFactory.make("nvvideoconvert", "convertor")
    if not nvvidconv:
        sys.stderr.write(" Unable to create nvvidconv \n")
    print("Creating nvosd \n ")
    nvosd = Gst.ElementFactory.make("nvdsosd", "onscreendisplay")
    if not nvosd:
        sys.stderr.write(" Unable to create nvosd \n")
    nvosd.set_property('process-mode', OSD_PROCESS_MODE)
    nvosd.set_property('display-text', OSD_DISPLAY_TEXT)
    nvosd.set_property('display-mask', True)
    if (is_aarch64()):
        print("Creating transform \n ")
        transform = Gst.ElementFactory.make(
            "nvegltransform", "nvegl-transform")
        if not transform:
            sys.stderr.write(" Unable to create transform \n")

    print("Creating EGLSink \n")
    sink = Gst.ElementFactory.make("nveglglessink", "nvvideo-renderer")
    if not sink:
        sys.stderr.write(" Unable to create egl sink \n")

    if is_live:
        print("Atleast one of the sources is live")
        streammux.set_property('live-source', 1)

    streammux.set_property('width', 640)
    streammux.set_property('height', 480)
    streammux.set_property('batch-size', number_sources)
    streammux.set_property('batched-push-timeout', 4000000)
    streammux.set_property('live-source', 1)
    pgie.set_property('config-file-path',
                      "config.txt")
    pgie.set_property('interval', 10)
    pgie_batch_size = pgie.get_property("batch-size")
    print("the batch size is", pgie_batch_size)
    if (pgie_batch_size != number_sources):
        print("WARNING: Overriding infer-config batch-size",
              pgie_batch_size, " with number of sources ", number_sources, " \n")
        pgie.set_property("batch-size", number_sources)
    tiler_rows = int(math.sqrt(number_sources))
    tiler_columns = int(math.ceil((1.0*number_sources)/tiler_rows))
    tiler.set_property("rows", tiler_rows)
    tiler.set_property("columns", tiler_columns)
    tiler.set_property("width", TILED_OUTPUT_WIDTH)
    tiler.set_property("height", TILED_OUTPUT_HEIGHT)
    # sink.set_property("qos", 0)
    sink.set_property("sync", 0)
    tracker.set_property('tracker-width', 640)

    tracker.set_property('tracker-height', 480)

    tracker.set_property('gpu_id', 0)

    tracker.set_property(
        'll-lib-file', "/opt/nvidia/deepstream/deepstream-7.0/lib/libnvds_nvmultiobjecttracker.so")

    print("Adding elements to Pipeline \n")
    pipeline.add(pgie)  # nvinfer
    pipeline.add(tracker)  # tracking
    pipeline.add(tiler)  # display windows
    pipeline.add(nvvidconv)
    pipeline.add(nvosd)  # display output
    if is_aarch64():
        pipeline.add(transform)
    pipeline.add(sink)

    print("Linking elements in the Pipeline \n")
    streammux.link(queue1)
    queue1.link(pgie)
    pgie.link(tracker)
    tracker.link(queue2)
    queue2.link(tiler)
    tiler.link(queue3)
    queue3.link(nvvidconv)
    nvvidconv.link(queue4)
    queue4.link(nvosd)
    if is_aarch64():
        nvosd.link(queue5)
        queue5.link(transform)
        transform.link(sink)
    else:
        nvosd.link(queue5)
        queue5.link(sink)

    # create an event loop and feed gstreamer bus mesages to it
    loop = GObject.MainLoop()
    bus = pipeline.get_bus()
    bus.add_signal_watch()
    bus.connect("message", bus_call, loop)
    tiler_src_pad = pgie.get_static_pad("src")
    if not tiler_src_pad:
        sys.stderr.write(" Unable to get src pad \n")
    else:
        tiler_src_pad.add_probe(Gst.PadProbeType.BUFFER,
                                tiler_src_pad_buffer_probe, 0)

    # List the sources
    print("Now playing...")
    for i, source in enumerate(args):
        if (i != 0):
            print(i, ": ", source)

    print("Starting pipeline \n")
    # start play back and listed to events
    pipeline.set_state(Gst.State.PLAYING)
    try:
        loop.run()
    except Exception:
        pass
    # cleanup
    print("Exiting app\n")
    pipeline.set_state(Gst.State.NULL)


if __name__ == '__main__':
    sys.exit(main(sys.argv))
