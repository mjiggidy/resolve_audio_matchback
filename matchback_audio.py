"""
Audio Matcher Backer v0.1
Written by Michael Jordan <michael@glowingpixel.com>

Given a V1 timeline, kinda sorta cut in embedded audio from V1 into A1 if it works.
"""

from __future__ import annotations
import typing, sys, json

if typing.TYPE_CHECKING:
	from resolvecommon.session import resolve
	import DaVinciResolveScript as bmd

resolve:bmd.Resolve

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

if total_count < 1:
	print("No clips found in V1.", file=sys.stderr)
	sys.exit(2)

counter = 0

for track_item in track_items:

	counter += 1

	print(f"[{str(counter).rjust(len(str(total_count)))} / {total_count}]", end="\r")

	timeline_start  = track_item.GetStart()
	source_item     = track_item.GetMediaPoolItem()

	if not source_item:
		print(f"* Skipped {track_item.GetName()}: Does not exist in media pool")
		continue

	source_start    = track_item.GetSourceStartFrame()
	source_end      = track_item.GetSourceEndFrame()
	source_audio_mapping = json.loads(source_item.GetAudioMapping())

	if source_audio_mapping.get("embedded_audio_channels", 0) == 0:
		print(f"* Skipped {track_item.GetName()}: No sync audio (MOS)")
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
		print(f"* ")