from typing import Any, Dict, Optional
from rest_framework.exceptions import ValidationError
from pyfacebook.api import GraphAPI

class FacebookService:
    """
    A service to deal with Facebook, including verification and fetching data.
    """

    @staticmethod
    def validate_facebook_account(user_access_token, facebook_user_id):
        """
        Check the authenticity of the token and user ID on Facebook.
        """
        try:
            api = GraphAPI(access_token=user_access_token)
            user_data = api.get_object(object_id="me", fields="id")

            if str(user_data["id"]) != facebook_user_id:
                raise ValidationError("facebook_user_id does not match the token's user.")
        except Exception as e:
            raise ValidationError(f"Error validating Facebook account: {e}")

    @staticmethod
    def fetch_facebook_user_data(user_access_token):
        """
        Fetch user data from Facebook.
        """
        try:
            api = GraphAPI(access_token=user_access_token)
            user_data = api.get_object(
                object_id="me",
                fields="id,name,picture,email"
            )
            return user_data
        except Exception as e:
            raise ValueError(f"Error fetching user data: {e}")

    @staticmethod
    def fetch_facebook_user_pages(user_access_token):
        """
        Fetch data for pages associated with your Facebook account.
        """
        try:
            api = GraphAPI(access_token=user_access_token)
            pages_data = api.get_connection(
                object_id="me",
                connection="accounts",
                fields="id,name,access_token,followers_count"
            )
            return pages_data
        except Exception as e:
            raise ValueError(f"Error fetching pages data: {e}")
        

    @staticmethod
    def fetch_facebook_user_info(user_access_token,facebook_user_id ):
        """
        Fetch data for account of user associated with your Facebook account.
        """
        try:
            api = GraphAPI(access_token=user_access_token, )
            data = api.get_object(
                object_id="me",
                fields=r"id,name,picture{url},accounts{id,name,global_brand_page_name,picture{url},access_token,category,followers_count,fan_count,tasks}"
            )
            return data
        except Exception as e:
            raise ValueError(f"Error fetching pages data: {e}")

    @staticmethod
    def post(
    access_token: str, 
    page_id: str, 
    post_message: str, 
    at_time: Optional[str] = None, 
    image_path: Optional[str] = None, 
    link: Optional[str] = None
    ): 
        """
        This function is for posting on Facebook with support for multiple cases e.g: scheduling status, attaching a picture, or posting at the moment
        
        :param access_token: Token access with the necessary permissions.
        :param page_id: Page ID.
        :param post_message: Content of the post.
        :param image_path: Local image path if any.
        :param at_time: Unix timestamp for scheduling the post.
        :param link: Optional link to include in the post.
        """
        # Initialize the Facebook Graph API
        graph = GraphAPI(access_token=access_token)

        # Ensure `at_time` is a valid Unix timestamp if provided
        if at_time:
            try:
                at_time = int(at_time)
            except ValueError:
                raise ValueError("The 'at_time' parameter must be a valid Unix timestamp.")

        # Prepare parameters for the post
        params = {
            "message": post_message,
            "link": link,
            "scheduled_publish_time": at_time,
            "published": "false" if at_time else "true",
        }

        # If an image is provided, post it
        if image_path:
            try:
                with open(image_path, 'rb') as image_file:
                    files = {'source': image_file}  # Attach the image file
                    response = graph.post_object(
                        object_id=page_id,
                        connection="photos",
                        params=params,
                        files=files
                    )
                return f"Photo uploaded successfully: {response}"
            except FileNotFoundError as e:
                raise FileNotFoundError(f"Image file not found: {e}")
            except Exception as e:
                raise RuntimeError(f"An error occurred while uploading the photo: {e}")

        # Otherwise, post text or link content
        try:
            response = graph.post_object(
                object_id=page_id,
                connection="feed",
                params=params
            )
            return f"Post uploaded successfully: {response}"
        except Exception as e:
            raise RuntimeError(f"An error occurred while posting: {e}")

    @staticmethod 
    def update_post(access_token: str, page_post_id: str, post_message: str):
        """
        Updates a Facebook post with new content.

        :param access_token: Access token with the necessary permissions.
        :param page_post_id: The ID of the post to be updated.
        :param post_message: The new message content for the post.
        :return: A success message or raises an error if the update fails.
        """


        # Initialize the Facebook Graph API
        graph = GraphAPI(access_token=access_token)

        # Parameters for the update
        params = {
            "message": post_message,
        }

        try:
            # Update the post
            response = graph.post_object(
                    object_id=page_post_id,
                    params=params
                )

            # Check if the response indicates success
            if response.get("success", False):
                return f"Post updated successfully: {response}"
            else:
                raise RuntimeError(f"Failed to update the post: {response}")
        except Exception as e:
            raise RuntimeError(f"An error occurred while updating the post: {e}")
        
    @staticmethod
    def delete_post(access_token: str, post_id: str):
        """
        Deletes a Facebook post by its ID.

        :param access_token: Access token with the necessary permissions.
        :param post_id: The ID of the post to be deleted.
        :return: A success message if the post is deleted, raises an error otherwise.
        """

        # Initialize the Facebook Graph API
        graph = GraphAPI(access_token=access_token)

        try:
            # Make the API call to delete the post
            response = graph.delete_object(object_id=post_id)

            # Check if the operation was successful
            if response.get("success", False):
                return f"Post with ID {post_id} deleted successfully."
            else:
                raise RuntimeError(f"Failed to delete the post with ID {post_id}. Response: {response}")

        except Exception as e:
            raise RuntimeError(f"An error occurred while deleting the post: {e}")
        
    def get_facebook_posts(access_token: str, page_id: str, fields: Optional[str] = None, limit: int = 10) -> Dict[str, Any]:
        """
        Fetch posts from a Facebook page using its ID.

        :param access_token: The access token with the required permissions.
        :param page_id: The ID of the Facebook page.
        :param fields: Comma-separated list of fields to fetch. Defaults to commonly used fields.
        :param limit: Maximum number of posts to fetch. Default is 10.
        :return: A dictionary containing the posts' data.
        :raises RuntimeError: If an error occurs during the API call.
        """
        if not access_token or not page_id:
            raise ValueError("Access token and page ID are required.")

        # Default fields if not provided
        fields = fields or "id,message,created_time,updated_time,from,full_picture,is_published,shares,permalink_url,status_type,likes"

        # Initialize the Facebook Graph API
        graph = GraphAPI(access_token=access_token)

        try:
            # Fetch posts with optional pagination
            posts = graph.get_object(
                f"{page_id}/posts", 
                fields=fields, 
                limit=limit
            )
            return posts

        except Exception as e:
            raise RuntimeError(f"Failed to fetch posts for page {page_id}: {e}")

    @staticmethod
    def get_info_post(access_token: str, post_id: str, fields: Optional[str] = None) -> dict:
        """
        Fetch detailed information about a specific Facebook post using its ID.

        :param access_token: The access token with the required permissions.
        :param post_id: The ID of the post to retrieve information for.
        :param fields: Comma-separated list of fields to fetch. Defaults to commonly used fields.
        :return: A dictionary containing the post's details.
        :raises RuntimeError: If an error occurs while fetching the post.
        """
        if not access_token or not post_id:
            raise ValueError("Access token and post ID are required and cannot be empty.")

        # Initialize the Facebook Graph API
        graph = GraphAPI(access_token=access_token)

        # Default fields if not provided
        fields = fields or "id,message,created_time,updated_time,likes,full_picture,is_published,shares,permalink_url,status_type,attachments"

        try:
            # Make the API call
            post_info = graph.get_object(object_id=post_id, fields=fields)

            return post_info

        except Exception as e:
            print(f"Error occurred while fetching post ID {post_id}: {e}")
            raise RuntimeError(f"An error occurred while fetching the post: {e}")


