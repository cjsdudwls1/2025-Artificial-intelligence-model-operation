# GitHub에 업로드하는 방법

이 프로젝트를 GitHub에 "Fast API_Userguide"라는 이름으로 업로드하려면 다음 단계를 따르세요.

## 1단계: GitHub에서 새 저장소 만들기

1. [GitHub](https://github.com)에 로그인합니다.
2. 우측 상단의 `+` 아이콘을 클릭하고 "New repository"를 선택합니다.
3. Repository name에 `Fast API_Userguide` 또는 `FastAPI-Userguide`를 입력합니다.
   (공백보다는 하이픈 사용을 권장합니다: `FastAPI-Userguide`)
4. Description(선택사항)에 "FastAPI 공식 자습서 예제 코드 모음"을 입력합니다.
5. Public 또는 Private을 선택합니다.
6. **"Add a README file"을 체크하지 마세요** (이미 README.md가 있습니다)
7. "Create repository" 버튼을 클릭합니다.

## 2단계: 로컬 저장소를 GitHub에 연결

GitHub에서 새 저장소를 만든 후, 다음 명령어들을 실행하세요:

```bash
# GitHub 저장소를 원격으로 추가 (아래 URL을 실제 저장소 URL로 변경하세요)
git remote add origin https://github.com/YOUR_USERNAME/FastAPI-Userguide.git

# 또는 SSH를 사용하는 경우:
# git remote add origin git@github.com:YOUR_USERNAME/FastAPI-Userguide.git

# 기본 브랜치 이름을 main으로 변경 (선택사항)
git branch -M main

# GitHub에 푸시
git push -u origin main
```

## 3단계: GitHub 인증

푸시할 때 인증이 필요할 수 있습니다:

### Personal Access Token 사용 (권장)
1. GitHub > Settings > Developer settings > Personal access tokens > Tokens (classic)
2. "Generate new token" 클릭
3. repo 권한 선택
4. 토큰 생성 후 복사
5. git push 시 비밀번호 대신 토큰을 입력

### SSH 키 사용
```bash
# SSH 키 생성 (이미 있다면 건너뛰기)
ssh-keygen -t ed25519 -C "your_email@example.com"

# SSH 키를 GitHub에 추가
# ~/.ssh/id_ed25519.pub 내용을 복사하여
# GitHub > Settings > SSH and GPG keys > New SSH key에 추가
```

## 완료!

이제 다음 URL에서 프로젝트를 확인할 수 있습니다:
`https://github.com/YOUR_USERNAME/FastAPI-Userguide`

## 추가 업데이트

프로젝트를 수정한 후 다시 푸시하려면:

```bash
git add .
git commit -m "업데이트 메시지"
git push
```

