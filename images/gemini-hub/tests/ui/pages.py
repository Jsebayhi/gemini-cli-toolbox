from playwright.sync_api import Page, expect

class LaunchWizard:
    """Component representing the 'New Session' wizard."""
    def __init__(self, page: Page):
        self.page = page
        self.root_list = page.locator("#roots-list")
        self.folder_list = page.locator("#folder-list")
        self.current_path = page.locator("#current-path")
        self.use_folder_btn = page.get_by_role("button", name="Use This Folder")
        self.launch_btn = page.get_by_role("button", name="Launch Session")
        self.task_input = page.get_by_placeholder("e.g. write a hello world in python...")
        self.variant_select = page.locator("#image-variant-select")
        self.worktree_check = page.get_by_label("Launch in Ephemeral Worktree")
        self.worktree_name_input = page.get_by_placeholder("Optional: Branch/Worktree Name")

    def select_root(self, path: str):
        self.root_list.get_by_text(path).click()

    def select_folder(self, name: str):
        self.folder_list.get_by_text(f"📁 {name}").click()

    def use_this_folder(self):
        self.use_folder_btn.click()

    def launch(self, task: str = None, variant: str = "standard"):
        self.use_folder_btn.click()
        if task:
            self.task_input.fill(task)
        self.variant_select.select_option(variant)
        self.launch_btn.click()

class HubPage:
    """Main Page Object for the Gemini Hub."""
    def __init__(self, page: Page, base_url: str):
        self.page = page
        self.base_url = base_url
        self.wizard = LaunchWizard(page)
        
        # Dashboard Locators
        self.new_session_btn = page.get_by_role("button", name="+ New Session")
        self.project_filter = page.get_by_placeholder("Search sessions...")
        self.type_filter = page.locator("#typeFilter")

    def navigate(self):
        self.page.goto(self.base_url)

    def open_wizard(self):
        self.new_session_btn.click()
        expect(self.page.get_by_text("Select a workspace root:")).to_be_visible()

    def stop_session(self, project_name: str):
        card = self.page.locator(".card", has_text=project_name)
        self.page.on("dialog", lambda dialog: dialog.accept())
        card.get_by_role("button", name="Stop").click()

    def expect_inactive_session(self, project_name: str):
        """Semantic check for an inactive/stopped session card."""
        card = self.page.locator(".card", has_text=project_name)
        expect(card).to_have_css("opacity", "0.5")
        expect(card.get_by_role("button", name="Stopped")).to_be_visible()

    def expect_active_session(self, project_name: str):
        """Semantic check for a healthy, active session card."""
        card = self.page.locator(".card", has_text=project_name)
        expect(card).to_have_css("opacity", "1")
        expect(card.get_by_role("button", name="Stop")).to_be_visible()
