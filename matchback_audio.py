"""
Audio Matcher Backer v0.1
Given a V1 timeline, kinda sorta cut in embedded audio from V1 into A1 if it works and stuff.

Written by Michael Jordan <michael@glowingpixel.com>
https://github.com/mjiggidy/resolve_audio_matchback/
"""

from __future__ import annotations
import typing, sys, json

# Just some lil' things for me heehee shh
if "resolve" not in globals():
	
	try:

		import DaVinciResolveScript as bmd
		resolve = bmd.scriptapp("Resolve")

	except:

		print("This script must be run from within Davinci Resolve.", file=sys.stderr)
		sys.exit(5)
try:

	current_project   = resolve.GetProjectManager().GetCurrentProject()
	current_mediapool = current_project.GetMediaPool()
	current_timeline  = current_project.GetCurrentTimeline()

	if not current_timeline:
		raise RuntimeError("No timeline currently loaded")

except Exception as e:
	
	print(f"Could not get current timeline: {e}", file=sys.stderr)
	sys.exit(1)

track_items = current_timeline.GetItemListInTrack("video", 1)
total_count = len(track_items)

# Not sure you CAN have 0 audio tracks, but just in case...
if current_timeline.GetTrackCount("audio") < 1:

	print("Inserting A1 Mono track")

	if not current_timeline.AddTrack("audio"):
		
		print("Could not create track A1 for some reason.", file=sys.stderr)
		sys.exit(3)

else:
	print("Audio track count is ", current_timeline.GetTrackCount("audio"))

if current_timeline.GetIsTrackLocked("audio", 1):

	print("A1 is locked.  Please unlock it to proceed.", file=sys.stderr)
	sys.exit(4)

if total_count < 1:
	
	print("No clips found in V1.", file=sys.stderr)
	sys.exit(2)

counter = 0

for track_item in track_items:

	counter += 1

	print(f"[{str(counter).rjust(len(str(total_count)))} / {total_count}]: ", end="")

	timeline_start  = track_item.GetStart()
	source_item     = track_item.GetMediaPoolItem()

	if not source_item:

		print(f"* Skipped {track_item.GetName()}: Does not exist in media pool", file=sys.stderr)
		continue

	source_start    = track_item.GetSourceStartFrame()
	source_end      = track_item.GetSourceEndFrame()
	source_audio_mapping = json.loads(source_item.GetAudioMapping())

	if source_audio_mapping.get("embedded_audio_channels", 0) == 0:

		print(f"* Skipped {track_item.GetName()}: No sync audio (MOS)", file=sys.stderr)
		continue

	insert_audio_info:bmd.AppendClipInfo = dict(
		mediaPoolItem = source_item,
		startFrame    = source_start,
		endFrame      = source_end,
		mediaType     = 2,
		trackIndex    = 1,
		recordFrame   = timeline_start
	)

	if not current_mediapool.AppendToTimeline([insert_audio_info]):

		print(f"*** {source_item.GetName()} not added, for unknown reasons", file=sys.stderr)
		continue

	print(f"{track_item.GetName()}", end="\r")