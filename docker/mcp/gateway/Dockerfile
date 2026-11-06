FROM alpine:3.24@sha256:be2656061b536c1883c4034790e21d0a09c5aaaf51968b89368a3c0371ea2c9a

# Alpine 公式パッケージの nginx（make scan-mcp-nginx の検査に合格した最新版）
RUN apk add --no-cache nginx=1.30.6-r0

# パッケージのファイル（/etc/nginx/nginx.conf など）は変更せず、gateway の設定は別の場所に置く
COPY nginx.conf /etc/gateway/nginx.conf
COPY conf.d/ /etc/gateway/conf.d/

STOPSIGNAL SIGQUIT
CMD ["nginx", "-c", "/etc/gateway/nginx.conf", "-g", "daemon off;"]
