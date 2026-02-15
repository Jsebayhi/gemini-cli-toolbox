from playwright.sync_api import Page, expect

class HubPage:
    """Page Object Model for the Gemini Hub UI."""
    
    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url
        
        # Locators
        self.new_session_btn = page.get_by_role("button", name="+ New Session")
        self.project_filter = page.get_by_placeholder("Search sessions...")
        self.type_filter = page.locator("#typeFilter")
        self.roots_list = page.locator("#roots-list")
        self.folder_list = page.locator("#folder-list")
        self.current_path = page.locator("#current-path")
        self.use_folder_btn = page.get_by_role("button", name="Use This Folder")
        self.launch_btn = page.get_by_role("button", name="Launch Session")
        self.done_btn = page.get_by_role("button", name="Done")
        self.task_input = page.get_by_placeholder("e.g. write a hello world in python...")
        self.image_variant_select = page.locator("#image-variant-select")
        self.profile_select = page.locator("#config-select")
        self.worktree_check = page.get_by_label("Launch in Ephemeral Worktree")
        self.worktree_name_input = page.get_by_placeholder("Optional: Branch/Worktree Name")
        self.advanced_toggle = page.get_by_text("Advanced Options")
        self.docker_args_input = page.get_by_placeholder("e.g. -v /host/path:/container/path")
        self.session_type_select = page.locator("#session-type-select")

    def navigate(self):
        self.page.goto(self.base_url)

    def open_wizard(self):
        self.new_session_btn.click()
        expect(self.page.get_by_text("Select a workspace root:")).to_be_visible()

    def select_root(self, path: str):
        self.roots_list.get_by_text(path).click()

    def select_folder(self, name: str):
        self.folder_list.get_by_text(f"📁 {name}").click()

    def use_this_folder(self):
        self.use_folder_btn.click()

    def launch(self, task: str = None, variant: str = None, profile: str = None):
        if task:
            self.task_input.fill(task)
        if variant:
            self.image_variant_select.select_option(variant)
        if profile:
            self.profile_select.select_option(profile)
        self.launch_btn.click()

    def stop_session(self, project_name: str):
        card = self.page.locator(".card", has_text=project_name)
        # Register dialog handler
        self.page.on("dialog", lambda dialog: dialog.accept())
        card.get_by_role("button", name="Stop").click()
