ニュートラルニュース Ver.1.7（iPhone・外出先対応）

この版はVer.1.6とは別の、GitHub Pages用の静的Webアプリです。
MacのFastAPIサーバーは不要です。記事はGitHub Actionsが定期取得してdocs/news.jsonに保存します。

【初回の準備】
1. https://github.com/ で無料アカウントを作成（既にあれば不要）。
2. GitHubで「New repository」→名前は neutral-news → Public → Create repository。
   注意：Publicは誰でも閲覧可能です。個人情報やパスワードはアップロードしないでください。
3. ZIPを解凍し、neutral_news_v17 フォルダの中身をリポジトリのルートにアップロードします。
   docs フォルダ、.github フォルダ（隠しフォルダ）、generate_news.py、news_core.py が必要です。
   .github フォルダを落とすと自動更新できません。
   GitHub画面で Add file → Upload files → Commit changes を使えます。
4. Settings → Pages → Build and deployment → Source: Deploy from a branch
   → Branch: main /docs → Save。
5. Actions → ニュースの自動更新 → Run workflow で最初の記事取得を実行します。
   Actionsの使用許可が必要な場合はリポジトリの設定で許可してください。
6. 数分後、https://<GitHubユーザー名>.github.io/neutral-news/ をiPhoneのSafariで開きます。
   GitHub Pagesの公開URLはSettings → Pagesでも確認できます。
7. Safariの共有 → ホーム画面に追加。

【日々の利用】
- Macの起動は不要。iPhoneの通信環境があれば外出先でも使えます。
- ニュース取得は1日4回を目安に自動実行。GitHubのスケジュールは遅延・停止することがあります。
- 週の4テーマは月曜日を基準に選択。取得失敗時は前回の記事が残ります。
- スタンプはiPhoneのSafari内だけに保存。別の端末とは同期しません。
- 無料枠やGitHubのサービス条件は将来変わる可能性があります。
- RSSタイトルとリンクのみを掲載。賛否の分類はしていません。

【安全と公開範囲】
GitHub Pagesは一般公開のサイトです。アカウント情報、住所、閲覧履歴などをリポジトリに入れないでください。
記録はサーバーに送信しません。URLは第三者が閲覧できます。
アプリのコードは公開されます。自分専用の非公開サービスではありません。

【Ver.1.6との関係】
Ver.1.6のMac用フォルダには触れません。記録も自動移行・同期しません。
