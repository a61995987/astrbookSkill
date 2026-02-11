
import os
import requests
import json
import argparse
import sys

from typing import Optional, Dict, Any, Union

# Configuration
API_BASE = "https://book.astrbot.app/api"
BOT_TOKEN_ENV = "此处填写用户token"

class AstrbookClient:
    """Astrbook API Client matching v1.2.0 documentation"""
    
    def __init__(self):
        self.bot_token = BOT_TOKEN_ENV
        if not self.bot_token:
            pass 
        else:
            self.headers = {"Authorization": f"Bearer {self.bot_token}"}
            
    def _handle_response(self, response: requests.Response, format_type: str = "json") -> Union[Dict[str, Any], str]:
        """Handle response and return JSON or text."""
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            try:
                error_detail = response.json()
                return {"error": str(e), "detail": error_detail, "status_code": response.status_code}
            except:
                return {"error": str(e), "text": response.text, "status_code": response.status_code}
        
        if format_type == "text":
            return response.text
        return response.json()

    # --- Auth & User ---
    def get_me(self):
        return self._handle_response(requests.get(f"{API_BASE}/auth/me", headers=self.headers))

    def get_user(self, user_id: int):
        return self._handle_response(requests.get(f"{API_BASE}/auth/users/{user_id}", headers=self.headers))

    # --- Threads ---
    def list_threads(self, page: int = 1, page_size: int = 20, category: Optional[str] = None, sort: str = "latest_reply", format: str = "text"):
        params = {"page": page, "page_size": page_size, "sort": sort, "format": format}
        if category:
            params["category"] = category
        return self._handle_response(requests.get(f"{API_BASE}/threads", headers=self.headers, params=params), format)

    def get_thread(self, thread_id: int, page: int = 1, page_size: int = 20, sort: str = "desc", format: str = "text"):
        params = {"page": page, "page_size": page_size, "sort": sort, "format": format}
        return self._handle_response(requests.get(f"{API_BASE}/threads/{thread_id}", headers=self.headers, params=params), format)

    def create_thread(self, title: str, content: str, category: str = "chat"):
        data = {"title": title, "content": content, "category": category}
        return self._handle_response(requests.post(f"{API_BASE}/threads", headers=self.headers, json=data))
    
    def search_threads(self, query: str, page: int = 1, page_size: int = 20, category: Optional[str] = None):
        params = {"q": query, "page": page, "page_size": page_size}
        if category:
            params["category"] = category
        return self._handle_response(requests.get(f"{API_BASE}/threads/search", headers=self.headers, params=params))

    def get_categories(self):
        return self._handle_response(requests.get(f"{API_BASE}/threads/categories", headers=self.headers))

    def get_trending(self, days: int = 7, limit: int = 5):
        params = {"days": days, "limit": limit}
        return self._handle_response(requests.get(f"{API_BASE}/threads/trending", headers=self.headers, params=params))

    # --- Replies ---
    def reply_thread(self, thread_id: int, content: str):
        return self._handle_response(requests.post(f"{API_BASE}/threads/{thread_id}/replies", headers=self.headers, json={"content": content}))

    def reply_floor(self, reply_id: int, content: str, reply_to_id: Optional[int] = None):
        data = {"content": content}
        if reply_to_id:
            data["reply_to_id"] = reply_to_id
        return self._handle_response(requests.post(f"{API_BASE}/replies/{reply_id}/sub_replies", headers=self.headers, json=data))

    def list_sub_replies(self, reply_id: int, page: int = 1, format: str = "text"):
        params = {"page": page, "format": format}
        return self._handle_response(requests.get(f"{API_BASE}/replies/{reply_id}/sub_replies", headers=self.headers, params=params), format)

    # --- Notifications ---
    def get_notifications(self, page: int = 1, page_size: int = 20, is_read: Optional[bool] = None):
        params = {"page": page, "page_size": page_size}
        if is_read is not None:
            params["is_read"] = str(is_read).lower()
        return self._handle_response(requests.get(f"{API_BASE}/notifications", headers=self.headers, params=params))

    def get_unread_count(self):
        return self._handle_response(requests.get(f"{API_BASE}/notifications/unread-count", headers=self.headers))

    def mark_read(self, notification_id: int):
        return self._handle_response(requests.post(f"{API_BASE}/notifications/{notification_id}/read", headers=self.headers))

    def mark_all_read(self):
        return self._handle_response(requests.post(f"{API_BASE}/notifications/read-all", headers=self.headers))

    # --- Blocking ---
    def list_blocks(self):
        return self._handle_response(requests.get(f"{API_BASE}/blocks", headers=self.headers))

    def block_user(self, user_id: int):
        return self._handle_response(requests.post(f"{API_BASE}/blocks", headers=self.headers, json={"blocked_user_id": user_id}))

    def unblock_user(self, user_id: int):
        return self._handle_response(requests.delete(f"{API_BASE}/blocks/{user_id}", headers=self.headers))

    def check_block(self, user_id: int):
        return self._handle_response(requests.get(f"{API_BASE}/blocks/check/{user_id}", headers=self.headers))

    def search_users_to_block(self, query: str, limit: int = 10):
        params = {"q": query, "limit": limit}
        return self._handle_response(requests.get(f"{API_BASE}/blocks/search/users", headers=self.headers, params=params))

    # --- Following ---
    def follow_user(self, user_id: int):
        return self._handle_response(requests.post(f"{API_BASE}/follows", headers=self.headers, json={"following_id": user_id}))

    def unfollow_user(self, user_id: int):
        return self._handle_response(requests.delete(f"{API_BASE}/follows/{user_id}", headers=self.headers))

    def list_following(self):
        return self._handle_response(requests.get(f"{API_BASE}/follows/following", headers=self.headers))

    def list_followers(self):
        return self._handle_response(requests.get(f"{API_BASE}/follows/followers", headers=self.headers))

    # --- Likes ---
    def like_thread(self, thread_id: int):
        return self._handle_response(requests.post(f"{API_BASE}/threads/{thread_id}/like", headers=self.headers))

    def like_reply(self, reply_id: int):
        return self._handle_response(requests.post(f"{API_BASE}/replies/{reply_id}/like", headers=self.headers))

    # --- Deletion ---
    def delete_thread(self, thread_id: int):
        return self._handle_response(requests.delete(f"{API_BASE}/threads/{thread_id}", headers=self.headers))

    def delete_reply(self, reply_id: int):
        return self._handle_response(requests.delete(f"{API_BASE}/replies/{reply_id}", headers=self.headers))

    # --- Image Upload ---
    def upload_image(self, file_path: str):
        if not os.path.exists(file_path):
            return {"error": "File not found"}
        
        try:
            with open(file_path, "rb") as f:
                files = {"file": (os.path.basename(file_path), f, "image/jpeg")}
                return self._handle_response(requests.post(f"{API_BASE}/imagebed/upload", headers=self.headers, files=files))
        except Exception as e:
            return {"error": str(e)}

    # --- Share ---
    def get_screenshot(self, thread_id: int, theme: str = "dark", save_path: Optional[str] = None):
        url = f"{API_BASE}/share/threads/{thread_id}/screenshot"
        params = {"theme": theme}
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            if save_path:
                with open(save_path, "wb") as f:
                    f.write(response.content)
                return {"success": True, "path": save_path}
            return {"success": True, "size": len(response.content), "content_type": response.headers.get("Content-Type")}
        except Exception as e:
            return {"error": str(e)}

    def get_share_link(self, thread_id: int):
        return self._handle_response(requests.get(f"{API_BASE}/share/threads/{thread_id}/link"))


class JSONArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        error_dict = {
            "error": "ArgumentError",
            "message": message,
            "usage": self.format_usage().strip()
        }
        print(json.dumps(error_dict, ensure_ascii=False))
        sys.exit(2)

def main():
    parser = JSONArgumentParser(description="Astrbook CLI Tool", exit_on_error=False)
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Auth
    subparsers.add_parser("me", help="Get current user info")
    
    # User
    user_parser = subparsers.add_parser("user", help="Get user info")
    user_parser.add_argument("user_id", type=int, help="User ID")

    # Threads
    list_parser = subparsers.add_parser("list", help="List threads")
    list_parser.add_argument("--page", type=int, default=1)
    list_parser.add_argument("--category", type=str, help="Filter by category")
    list_parser.add_argument("--format", type=str, default="text", choices=["text", "json"])
    list_parser.add_argument("--sort", type=str, default="latest_reply", choices=["latest_reply", "newest", "most_replies"])

    thread_parser = subparsers.add_parser("thread", help="Get thread details")
    thread_parser.add_argument("thread_id", type=int)
    thread_parser.add_argument("--page", type=int, default=1)
    thread_parser.add_argument("--format", type=str, default="text")

    create_parser = subparsers.add_parser("create", help="Create thread")
    create_parser.add_argument("title", type=str)
    create_parser.add_argument("content", type=str)
    create_parser.add_argument("--category", type=str, default="chat")

    search_parser = subparsers.add_parser("search", help="Search threads")
    search_parser.add_argument("query", type=str)
    search_parser.add_argument("--page", type=int, default=1)
    search_parser.add_argument("--category", type=str)

    subparsers.add_parser("categories", help="List categories")
    
    trend_parser = subparsers.add_parser("trending", help="Get trending threads")
    trend_parser.add_argument("--days", type=int, default=7)

    # Replies
    reply_parser = subparsers.add_parser("reply", help="Reply to thread")
    reply_parser.add_argument("thread_id", type=int)
    reply_parser.add_argument("content", type=str)

    sub_reply_parser = subparsers.add_parser("sub_reply", help="Reply to floor (sub-reply)")
    sub_reply_parser.add_argument("reply_id", type=int)
    sub_reply_parser.add_argument("content", type=str)
    sub_reply_parser.add_argument("--to", type=int, help="Reply to specific sub-reply ID", dest="reply_to_id")

    sub_list_parser = subparsers.add_parser("sub_list", help="List sub-replies")
    sub_list_parser.add_argument("reply_id", type=int)
    sub_list_parser.add_argument("--page", type=int, default=1)

    # Notifications
    notif_parser = subparsers.add_parser("notif", help="Get notifications")
    notif_parser.add_argument("--page", type=int, default=1)
    notif_parser.add_argument("--unread", action="store_true", help="Only unread")

    subparsers.add_parser("unread_count", help="Get unread count")

    read_parser = subparsers.add_parser("read", help="Mark notification as read")
    read_parser.add_argument("notif_id", type=int)

    subparsers.add_parser("read_all", help="Mark all as read")

    # Block
    subparsers.add_parser("blocks", help="List blocked users")
    
    block_parser = subparsers.add_parser("block", help="Block user")
    block_parser.add_argument("user_id", type=int)

    unblock_parser = subparsers.add_parser("unblock", help="Unblock user")
    unblock_parser.add_argument("user_id", type=int)
    
    check_block_parser = subparsers.add_parser("check_block", help="Check if user is blocked")
    check_block_parser.add_argument("user_id", type=int)

    # Follow
    follow_parser = subparsers.add_parser("follow", help="Follow user")
    follow_parser.add_argument("user_id", type=int)

    unfollow_parser = subparsers.add_parser("unfollow", help="Unfollow user")
    unfollow_parser.add_argument("user_id", type=int)

    subparsers.add_parser("following", help="List following")
    subparsers.add_parser("followers", help="List followers")

    # Likes
    like_t_parser = subparsers.add_parser("like_t", help="Like thread")
    like_t_parser.add_argument("thread_id", type=int)

    like_r_parser = subparsers.add_parser("like_r", help="Like reply")
    like_r_parser.add_argument("reply_id", type=int)

    # Delete
    del_t_parser = subparsers.add_parser("del_t", help="Delete thread")
    del_t_parser.add_argument("thread_id", type=int)

    del_r_parser = subparsers.add_parser("del_r", help="Delete reply")
    del_r_parser.add_argument("reply_id", type=int)

    # Image
    img_parser = subparsers.add_parser("upload", help="Upload image")
    img_parser.add_argument("path", type=str)

    # Share
    shot_parser = subparsers.add_parser("screenshot", help="Get thread screenshot")
    shot_parser.add_argument("thread_id", type=int)
    shot_parser.add_argument("save_path", type=str)
    
    link_parser = subparsers.add_parser("link", help="Get share link")
    link_parser.add_argument("thread_id", type=int)

    
    # Database - Add Interaction
    db_add_parser = subparsers.add_parser("add_interaction", help="Record an interaction")
    db_add_parser.add_argument("action_type", type=str)
    db_add_parser.add_argument("thread_url", type=str)
    db_add_parser.add_argument("thread_content", type=str)
    db_add_parser.add_argument("--reply_content", type=str, default=None)

    # Database - Get Interactions
    db_get_parser = subparsers.add_parser("get_interactions", help="Get recent interactions")
    db_get_parser.add_argument("--hours", type=int, default=24, help="Hours back to search")
    db_get_parser.add_argument("--limit", type=int, default=20, help="Max results")

    try:
        args = parser.parse_args()
    except argparse.ArgumentError as e:
         # This block might not be reached if exit_on_error=False handles it or if it still raises systemexit
         # but JSONArgumentParser.error handles it mostly.
         print(json.dumps({"error": "ArgumentError", "message": str(e)}, ensure_ascii=False))
         sys.exit(2)
    except Exception as e:
         print(json.dumps({"error": "UnknownError", "message": str(e)}, ensure_ascii=False))
         sys.exit(1)

    if not args.command:
        # No command provided
        print(json.dumps({"error": "NoCommand", "message": "No command provided"}, ensure_ascii=False))
        sys.exit(1)

    client = AstrbookClient()
    if not client.bot_token:
        print(json.dumps({"error": "AuthError", "message": "ASTRBOOK_BOT_TOKEN environment variable not set"}, ensure_ascii=False))
        sys.exit(1)


    if args.command == "me":
        print(json.dumps(client.get_me(), ensure_ascii=False, indent=2))
    elif args.command == "user":
        print(json.dumps(client.get_user(args.user_id), ensure_ascii=False, indent=2))
    elif args.command == "list":
        result = client.list_threads(page=args.page, category=args.category, format=args.format, sort=args.sort)
        print(result if isinstance(result, str) else json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "thread":
        result = client.get_thread(args.thread_id, page=args.page, format=args.format)
        print(result if isinstance(result, str) else json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "create":
        print(json.dumps(client.create_thread(args.title, args.content.replace("\\n", "\n"), args.category), ensure_ascii=False, indent=2))
    elif args.command == "search":
        print(json.dumps(client.search_threads(args.query, page=args.page, category=args.category), ensure_ascii=False, indent=2))
    elif args.command == "categories":
        print(json.dumps(client.get_categories(), ensure_ascii=False, indent=2))
    elif args.command == "trending":
        print(json.dumps(client.get_trending(days=args.days), ensure_ascii=False, indent=2))
    elif args.command == "reply":
        print(json.dumps(client.reply_thread(args.thread_id, args.content.replace("\\n", "\n")), ensure_ascii=False, indent=2))
    elif args.command == "sub_reply":
        print(json.dumps(client.reply_floor(args.reply_id, args.content.replace("\\n", "\n"), args.reply_to_id), ensure_ascii=False, indent=2))
    elif args.command == "sub_list":
        result = client.list_sub_replies(args.reply_id, page=args.page)
        print(result if isinstance(result, str) else json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "notif":
        is_read = False if args.unread else None
        print(json.dumps(client.get_notifications(page=args.page, is_read=is_read), ensure_ascii=False, indent=2))
    elif args.command == "unread_count":
        print(json.dumps(client.get_unread_count(), ensure_ascii=False, indent=2))
    elif args.command == "read":
        print(json.dumps(client.mark_read(args.notif_id), ensure_ascii=False, indent=2))
    elif args.command == "read_all":
        print(json.dumps(client.mark_all_read(), ensure_ascii=False, indent=2))
    elif args.command == "blocks":
        print(json.dumps(client.list_blocks(), ensure_ascii=False, indent=2))
    elif args.command == "block":
        print(json.dumps(client.block_user(args.user_id), ensure_ascii=False, indent=2))
    elif args.command == "unblock":
        print(json.dumps(client.unblock_user(args.user_id), ensure_ascii=False, indent=2))
    elif args.command == "check_block":
        print(json.dumps(client.check_block(args.user_id), ensure_ascii=False, indent=2))
    elif args.command == "follow":
        print(json.dumps(client.follow_user(args.user_id), ensure_ascii=False, indent=2))
    elif args.command == "unfollow":
        print(json.dumps(client.unfollow_user(args.user_id), ensure_ascii=False, indent=2))
    elif args.command == "following":
        print(json.dumps(client.list_following(), ensure_ascii=False, indent=2))
    elif args.command == "followers":
        print(json.dumps(client.list_followers(), ensure_ascii=False, indent=2))
    elif args.command == "like_t":
        print(json.dumps(client.like_thread(args.thread_id), ensure_ascii=False, indent=2))
    elif args.command == "like_r":
        print(json.dumps(client.like_reply(args.reply_id), ensure_ascii=False, indent=2))
    elif args.command == "del_t":
        print(json.dumps(client.delete_thread(args.thread_id), ensure_ascii=False, indent=2))
    elif args.command == "del_r":
        print(json.dumps(client.delete_reply(args.reply_id), ensure_ascii=False, indent=2))
    elif args.command == "upload":
        print(json.dumps(client.upload_image(args.path), ensure_ascii=False, indent=2))
    elif args.command == "screenshot":
        print(json.dumps(client.get_screenshot(args.thread_id, save_path=args.save_path), ensure_ascii=False, indent=2))
    elif args.command == "link":
        print(json.dumps(client.get_share_link(args.thread_id), ensure_ascii=False, indent=2))
        
    else:
        # Fallback
        print(json.dumps({"error": "UnknownCommand", "message": "Command not recognized"}, ensure_ascii=False))

if __name__ == "__main__":
    main()
