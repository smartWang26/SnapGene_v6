import os, json, urllib.request, datetime, smtplib, ssl
from email.message import EmailMessage

def main():
    password = os.environ.get('SMTP_PASSWORD')
    if not password:
        raise RuntimeError('请先配置 SMTP_PASSWORD（163邮箱SMTP授权码）')
    since = (datetime.datetime.now(datetime.timezone.utc)-datetime.timedelta(days=7)).isoformat()
    repo = os.environ['GITHUB_REPOSITORY']
    items = []
    for page in range(1, 101):
        url = f'https://api.github.com/repos/{repo}/issues?state=all&since={since}&per_page=100&page={page}'
        req = urllib.request.Request(url, headers={'Authorization':'Bearer '+os.environ['GH_TOKEN'], 'Accept':'application/vnd.github+json'})
        with urllib.request.urlopen(req, timeout=30) as r:
            batch = json.load(r)
        items.extend(i for i in batch if 'pull_request' not in i)
        if len(batch) < 100:
            break
    msg = EmailMessage()
    msg['Subject'] = 'SnapGene 每周反馈汇总 · wang26'
    msg['From'] = msg['To'] = 'wang_262026@163.com'
    msg.set_content('近7天新增或更新的反馈（含已关闭）：\n\n' + ('\n\n'.join(i['title']+'\n'+i['html_url']+'\n'+(i.get('body') or '')[:5000] for i in items) or '本周暂无反馈。'))
    with smtplib.SMTP_SSL('smtp.163.com', 465, context=ssl.create_default_context(), timeout=30) as server:
        server.login('wang_262026@163.com', password)
        server.send_message(msg)

if __name__ == '__main__':
    main()
