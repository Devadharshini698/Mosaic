"""Encode an authentic screenshot demo with synthetic narration and burned captions."""
import json, re, subprocess, wave
from pathlib import Path
import imageio_ffmpeg

root=Path(__file__).resolve().parents[1]; out=root/'artifacts/demo'
scenes=json.loads((out/'scenes.json').read_text(encoding='utf-8-sig'))
metadata=json.loads((out/'narration-metadata.json').read_text(encoding='utf-8'))
ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
def stamp(t):
    ms=round(t*1000); return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
durations=[]; audio_chunks=[]; fmt=None
for i,scene in enumerate(scenes):
    with wave.open(str(out/f'scene-{i}.wav'),'rb') as w:
        params=(w.getnchannels(),w.getsampwidth(),w.getframerate()); fmt=fmt or params
        assert params==fmt
        sound=w.readframes(w.getnframes()); duration=w.getnframes()/w.getframerate()
        pause=0.6
        audio_chunks.append(sound+b'\0'*(round(pause*fmt[2])*fmt[0]*fmt[1]))
        durations.append(duration+pause)
with wave.open(str(out/'narration.wav'),'wb') as w:
    w.setnchannels(fmt[0]);w.setsampwidth(fmt[1]);w.setframerate(fmt[2]);w.writeframes(b''.join(audio_chunks))
total=sum(durations); subtitles=[]; elapsed=0; idx=1
for scene_index,(scene,duration) in enumerate(zip(scenes,durations)):
    words=json.loads((out/f'boundaries-{scene_index}.json').read_text(encoding='utf-8'))
    source_words=scene['text'].split()
    if len(source_words)==len(words) and all(a.strip('.,:;!?').lower()==b['text'].lower() for a,b in zip(source_words,words)):
        words=[dict(boundary,text=original) for original,boundary in zip(source_words,words)]
    chunks=[]; current=[]
    for word in words:
        if len(' '.join(w['text'] for w in current+[word]))>88: chunks.append(current);current=[]
        current.append(word)
    if current:chunks.append(current)
    for chunk_index,chunk in enumerate(chunks):
        next_start=chunks[chunk_index+1][0]['start'] if chunk_index+1<len(chunks) else duration
        t=elapsed+chunk[0]['start']; end=elapsed+min(next_start,chunk[-1]['end']+.12,duration)
        chunk=[w['text'] for w in chunk]
        split=len(chunk)//2
        text=' '.join(chunk) if len(' '.join(chunk))<=48 else ' '.join(chunk[:split])+'\n'+' '.join(chunk[split:])
        subtitles.append(f'{idx}\n{stamp(t)} --> {stamp(end)}\n{text}\n');idx+=1
    elapsed+=duration
(out/'demo.srt').write_text('\n'.join(subtitles),encoding='utf-8')
(out/'transcript.md').write_text('# Mosaic Mix Lab demo transcript\n\nSynthetic neural voice: '+metadata['voice']+'. Natural speaking rate; authentic screenshots of the completed app.\n\n'+'\n\n'.join(s['text'] for s in scenes)+'\n',encoding='utf-8')
(out/'demo-script.md').write_text('# Demo shot list\n\n'+'\n\n'.join(f"{i+1}. {s['title']} ({durations[i]:.1f}s) — {s['image']}\n\n{s['text']}" for i,s in enumerate(scenes))+'\n',encoding='utf-8')
concat=''.join(f"file '{s['image']}'\nduration {duration:.6f}\n" for s,duration in zip(scenes,durations))+f"file '{scenes[-1]['image']}'\n"
(out/'images.ffconcat').write_text(concat,encoding='utf-8')
assert 90<=total<=120, f'Adjust narration rate; duration {total}'
cmd=[ffmpeg,'-y','-f','concat','-safe','0','-i','images.ffconcat','-i','narration.wav','-vf',"scale=1920:920:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:0:color=0x102d29,fps=24,subtitles=demo.srt:force_style='FontName=Arial,FontSize=12,PrimaryColour=&H00FFFFFF,OutlineColour=&H00292D10,BorderStyle=1,Outline=1,Shadow=0,Alignment=2,MarginV=12'",'-r','24','-c:v','libx264','-preset','fast','-crf','20','-pix_fmt','yuv420p','-c:a','aac','-b:a','128k','-t',str(total),'-movflags','+faststart','mosaic-mix-lab-demo.mp4']
subprocess.run(cmd,cwd=out,check=True,capture_output=True)
probe=subprocess.run([ffmpeg,'-i',str(out/'mosaic-mix-lab-demo.mp4'),'-af','volumedetect','-f','null','-'],capture_output=True,text=True)
assert '1920x1080' in probe.stderr and 'h264' in probe.stderr and 'aac' in probe.stderr
assert 'mean_volume: -inf' not in probe.stderr
for sec in [8,40,83,round(total-6)]:
    subprocess.run([ffmpeg,'-y','-ss',str(sec),'-i',str(out/'mosaic-mix-lab-demo.mp4'),'-frames:v','1',str(out/f'frame-{sec}.png')],check=True,capture_output=True)
validation={'durationSeconds':round(total,3),'resolution':'1920x1080','fps':24,'videoCodec':'H.264','audioCodec':'AAC 128kbps','pixelFormat':'yuv420p','fastStart':True,'captionCues':idx-1,'captions':'burned in and separate SRT, synchronized to provider word boundaries','voice':metadata['voice']+', synthetic neural','speakingRate':metadata['rate'],'scenes':len(scenes),'source':'Authentic app screenshots captured through browser tool','fileBytes':(out/'mosaic-mix-lab-demo.mp4').stat().st_size,'audioLevels':re.findall(r'(?:mean|max)_volume: [^\n]+',probe.stderr)}
(out/'validation.json').write_text(json.dumps(validation,indent=2),encoding='utf-8')
print(json.dumps(validation,indent=2))
