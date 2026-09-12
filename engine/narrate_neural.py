"""Natural neural narration with provider word timings; sends only the public demo script."""
import asyncio
import json
import subprocess
from pathlib import Path
import edge_tts
import imageio_ffmpeg

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts/demo'
VOICE='en-IN-NeerjaExpressiveNeural'

async def main():
    scenes=json.loads((OUT/'scenes.json').read_text(encoding='utf-8-sig'))
    voices=await edge_tts.list_voices()
    assert any(v['ShortName']==VOICE for v in voices), 'Requested neural voice is unavailable'
    for i,scene in enumerate(scenes):
        boundaries=[]
        speech=edge_tts.Communicate(scene['text'],VOICE,rate='+0%',boundary='WordBoundary',connect_timeout=15,receive_timeout=45)
        with (OUT/f'neural-{i}.mp3').open('wb') as audio:
            async for chunk in speech.stream():
                if chunk['type']=='audio': audio.write(chunk['data'])
                elif chunk['type']=='WordBoundary': boundaries.append({'start':chunk['offset']/1e7,'end':(chunk['offset']+chunk['duration'])/1e7,'text':chunk['text']})
        assert boundaries, f'No word timings for scene {i}'
        (OUT/f'boundaries-{i}.json').write_text(json.dumps(boundaries,indent=2),encoding='utf-8')
        subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-y','-i',str(OUT/f'neural-{i}.mp3'),'-ar','24000','-ac','1','-c:a','pcm_s16le',str(OUT/f'scene-{i}.wav')],check=True,capture_output=True)
        print(f'Scene {i+1}: neural audio and {len(boundaries)} word timings rendered',flush=True)
    (OUT/'narration-metadata.json').write_text(json.dumps({'voice':VOICE,'provider':'Microsoft Edge online neural text-to-speech','package':'edge-tts 7.2.8','synthetic':True,'rate':'+0%','captionTiming':'provider word boundaries'},indent=2),encoding='utf-8')

if __name__=='__main__': asyncio.run(main())
