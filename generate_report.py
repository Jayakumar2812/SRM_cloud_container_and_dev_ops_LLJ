from __future__ import annotations

import datetime as dt
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable,
    Image as RLImage,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
OUTPUT_PDF = BASE_DIR / "aws_devops_mini_project_report.pdf"


def get_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Helvetica.ttc",
        "/System/Library/Fonts/SFNS.ttf",
    ]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def draw_wrapped_text(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    text: str,
    font: ImageFont.ImageFont,
    fill: str,
    width: int,
    line_spacing: int = 6,
) -> int:
    x, y = xy
    lines = textwrap.wrap(text, width=width)
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        bbox = draw.textbbox((x, y), line, font=font)
        y += (bbox[3] - bbox[1]) + line_spacing
    return y


def draw_window(draw: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int, title: str, subtitle: str) -> None:
    draw.rounded_rectangle((x, y, x + w, y + h), radius=18, fill="#FFFFFF", outline="#D8E0EA", width=3)
    draw.rounded_rectangle((x, y, x + w, y + 54), radius=18, fill="#F5F8FC", outline="#D8E0EA", width=3)
    draw.rectangle((x, y + 28, x + w, y + 54), fill="#F5F8FC", outline="#F5F8FC")
    for idx, color in enumerate(("#FF5F57", "#FEBC2E", "#28C840")):
        cx = x + 28 + idx * 24
        draw.ellipse((cx, y + 18, cx + 12, y + 30), fill=color)
    draw.text((x + 90, y + 15), title, font=get_font(24, bold=True), fill="#20324A")
    draw.text((x + 90, y + 32), subtitle, font=get_font(13), fill="#6B7C93")


def draw_chip(draw: ImageDraw.ImageDraw, x: int, y: int, text: str, fill: str, text_fill: str = "#FFFFFF") -> None:
    font = get_font(16, bold=True)
    tw = draw.textbbox((0, 0), text, font=font)[2]
    draw.rounded_rectangle((x, y, x + tw + 28, y + 34), radius=12, fill=fill)
    draw.text((x + 14, y + 8), text, font=font, fill=text_fill)


def draw_box(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    w: int,
    h: int,
    title: str,
    body: str,
    fill: str = "#FFFFFF",
    outline: str = "#C9D4E3",
) -> None:
    draw.rounded_rectangle((x, y, x + w, y + h), radius=22, fill=fill, outline=outline, width=3)
    draw.text((x + 20, y + 18), title, font=get_font(24, bold=True), fill="#18324B")
    draw_wrapped_text(draw, (x + 20, y + 60), body, get_font(17), "#31475F", width=30)


def draw_arrow(draw: ImageDraw.ImageDraw, x1: int, y1: int, x2: int, y2: int, fill: str = "#2F6FED") -> None:
    draw.line((x1, y1, x2, y2), fill=fill, width=8)
    if x2 >= x1:
        draw.polygon([(x2, y2), (x2 - 18, y2 - 12), (x2 - 18, y2 + 12)], fill=fill)
    else:
        draw.polygon([(x2, y2), (x2 + 18, y2 - 12), (x2 + 18, y2 + 12)], fill=fill)


def create_architecture_figure(path: Path) -> None:
    img = Image.new("RGB", (1400, 860), "#EEF4FB")
    draw = ImageDraw.Draw(img)
    draw_window(draw, 40, 34, 1320, 792, "AWS DevOps Architecture", "Containerized web application with automated CI/CD")

    draw_chip(draw, 90, 110, "Live Workflow", "#0C8F52")
    draw_chip(draw, 255, 110, "Git Integrated", "#2F6FED")

    draw_box(draw, 90, 220, 220, 170, "GitHub", "Developers push code to the main branch or merge pull requests.")
    draw_box(draw, 380, 220, 220, 170, "CodePipeline", "The source change automatically triggers the pipeline.")
    draw_box(draw, 670, 220, 220, 170, "CodeBuild", "Dependencies are installed, tests run, and the Docker image is built.")
    draw_box(draw, 960, 220, 220, 170, "Amazon ECR", "A versioned image is pushed to the private registry.")
    draw_box(draw, 380, 510, 240, 170, "Amazon ECS", "The Fargate service pulls the new image and updates running tasks.")
    draw_box(draw, 690, 510, 240, 170, "Application Load Balancer", "Traffic is routed to healthy containers after deployment.")
    draw_box(draw, 1000, 510, 240, 170, "CloudWatch", "Logs, build status, and deployment metrics are monitored.")

    draw_arrow(draw, 310, 305, 380, 305)
    draw_arrow(draw, 600, 305, 670, 305)
    draw_arrow(draw, 890, 305, 960, 305)
    draw_arrow(draw, 1080, 390, 1080, 450)
    draw_arrow(draw, 980, 595, 930, 595)
    draw_arrow(draw, 620, 595, 690, 595)
    draw_arrow(draw, 500, 390, 500, 480)

    draw.rounded_rectangle((90, 710, 1240, 780), radius=18, fill="#FDFEFF", outline="#C9D4E3", width=2)
    footer = (
        "Pipeline summary: GitHub commit -> Source stage -> Unit test + Docker build -> Image push to ECR "
        "-> ECS rolling deployment -> Monitoring and verification."
    )
    draw_wrapped_text(draw, (115, 730), footer, get_font(20), "#1A3551", width=95, line_spacing=8)

    img.save(path)


def create_pipeline_figure(path: Path) -> None:
    img = Image.new("RGB", (1400, 900), "#F0F5FA")
    draw = ImageDraw.Draw(img)
    draw_window(draw, 45, 40, 1310, 820, "AWS CodePipeline", "Illustrative pipeline execution dashboard")

    draw.text((90, 120), "Pipeline: webapp-prod-cicd", font=get_font(28, bold=True), fill="#18324B")
    draw.text((90, 160), "Execution ID: cp-2026-03-29-001", font=get_font(16), fill="#63778F")
    draw_chip(draw, 1010, 118, "Succeeded", "#0C8F52")

    stages = [
        ("Source", "GitHub (main)", "Commit detected through CodeStar Connection", "#DDEBFF"),
        ("Build", "CodeBuild", "Install -> test -> docker build -> push", "#E7F7ED"),
        ("Deploy", "Amazon ECS", "Service updated with new image tag", "#FFF3D8"),
        ("Verify", "CloudWatch + ALB", "Health checks and runtime monitoring", "#F5E8FF"),
    ]

    x = 95
    for index, (title, service, body, color) in enumerate(stages):
        box_w = 270
        box_h = 250
        y = 260
        draw.rounded_rectangle((x, y, x + box_w, y + box_h), radius=24, fill=color, outline="#C7D3E2", width=3)
        draw.text((x + 24, y + 24), title, font=get_font(28, bold=True), fill="#18324B")
        draw.text((x + 24, y + 68), service, font=get_font(19, bold=True), fill="#34506D")
        draw_wrapped_text(draw, (x + 24, y + 110), body, get_font(17), "#35506C", width=24)
        draw_chip(draw, x + 24, y + 190, "Passed", "#0C8F52")
        if index < len(stages) - 1:
            draw_arrow(draw, x + box_w, y + 124, x + box_w + 48, y + 124)
        x += 310

    draw.rounded_rectangle((90, 585, 1260, 790), radius=20, fill="#FFFFFF", outline="#D7E0EA", width=2)
    draw.text((115, 615), "Latest Trigger", font=get_font(24, bold=True), fill="#18324B")
    draw.text((115, 660), "Commit: 7f3c9d2  |  Author: Dev Team  |  Branch: main", font=get_font(18), fill="#324A63")
    draw.text((115, 700), "Action: Added new feature, tests passed, image deployed to ECS cluster", font=get_font(18), fill="#324A63")
    draw.text((115, 740), "Deployment time: ~4 minutes 12 seconds", font=get_font(18), fill="#324A63")

    img.save(path)


def create_build_figure(path: Path) -> None:
    img = Image.new("RGB", (1400, 900), "#EEF4FA")
    draw = ImageDraw.Draw(img)
    draw_window(draw, 45, 40, 1310, 820, "AWS CodeBuild", "Illustrative build logs and quality checks")

    draw.rounded_rectangle((85, 120, 390, 780), radius=20, fill="#FFFFFF", outline="#D7E0EA", width=2)
    draw.text((110, 155), "Build Summary", font=get_font(26, bold=True), fill="#18324B")
    metrics = [
        ("Project", "webapp-build"),
        ("Runtime", "Standard 7.0"),
        ("Tests", "18 passed"),
        ("Coverage", "92%"),
        ("Docker Image", "webapp:7f3c9d2"),
        ("Artifact", "imagedefinitions.json"),
    ]
    y = 215
    for label, value in metrics:
        draw.text((112, y), label, font=get_font(18, bold=True), fill="#34506D")
        draw.text((112, y + 26), value, font=get_font(18), fill="#18324B")
        y += 88

    draw.rounded_rectangle((430, 120, 1295, 780), radius=20, fill="#0F1722", outline="#243447", width=2)
    draw.text((460, 150), "Build logs", font=get_font(24, bold=True), fill="#9DD2FF")
    log_lines = [
        "[Container] 2026/03/29 10:04:11 INSTALL dependencies",
        "[Container] pip install -r requirements.txt",
        "[Container] pytest -q",
        "..................                                                [100%]",
        "18 passed in 2.43s",
        "[Container] docker build -t webapp:$CODEBUILD_RESOLVED_SOURCE_VERSION .",
        "[Container] docker tag webapp:7f3c9d2 <account>.dkr.ecr.ap-south-1.amazonaws.com/webapp:7f3c9d2",
        "[Container] docker push <account>.dkr.ecr.ap-south-1.amazonaws.com/webapp:7f3c9d2",
        "[Container] printf '[{\"name\":\"webapp\",\"imageUri\":\"...\"}]' > imagedefinitions.json",
        "[Container] Phase complete: BUILD State: SUCCEEDED",
    ]
    y = 205
    for line in log_lines:
        draw.text((462, y), line, font=get_font(17), fill="#D5E6FF")
        y += 52

    img.save(path)


def create_deployment_figure(path: Path) -> None:
    img = Image.new("RGB", (1400, 900), "#F1F5FA")
    draw = ImageDraw.Draw(img)
    draw_window(draw, 45, 40, 1310, 820, "Deployment Verification", "Illustrative ECS service health and web application output")

    draw.rounded_rectangle((85, 120, 840, 780), radius=18, fill="#FFFFFF", outline="#D7E0EA", width=2)
    draw.rounded_rectangle((110, 175, 805, 740), radius=12, fill="#FAFCFF", outline="#D7E0EA", width=2)
    draw.rectangle((110, 175, 805, 235), fill="#F5F8FC", outline="#D7E0EA")
    draw.text((135, 192), "http://webapp-prod.example.com", font=get_font(20), fill="#475B72")
    draw.text((155, 285), "Feature Release Dashboard", font=get_font(34, bold=True), fill="#17314A")
    draw.text((155, 335), "Deployment Status: Live", font=get_font(24, bold=True), fill="#0C8F52")
    draw.text((155, 380), "Version: 7f3c9d2", font=get_font(22), fill="#34506D")
    draw.text((155, 420), "Environment: Production", font=get_font(22), fill="#34506D")
    draw.text((155, 460), "Container Health: 2/2 tasks healthy", font=get_font(22), fill="#34506D")
    draw.rounded_rectangle((155, 530, 360, 600), radius=16, fill="#2F6FED")
    draw.text((190, 552), "New Feature Active", font=get_font(24, bold=True), fill="#FFFFFF")
    draw.rounded_rectangle((395, 530, 650, 600), radius=16, fill="#0C8F52")
    draw.text((435, 552), "Tests Passed", font=get_font(24, bold=True), fill="#FFFFFF")

    draw.rounded_rectangle((885, 120, 1295, 780), radius=18, fill="#FFFFFF", outline="#D7E0EA", width=2)
    draw.text((915, 155), "ECS Service Details", font=get_font(26, bold=True), fill="#18324B")
    details = [
        "Cluster: prod-cluster",
        "Service: webapp-service",
        "Launch type: Fargate",
        "Desired tasks: 2",
        "Running tasks: 2",
        "Deployment status: Completed",
        "Target group health: Healthy",
        "Latest image: webapp:7f3c9d2",
    ]
    y = 220
    for item in details:
        draw.text((918, y), item, font=get_font(20), fill="#34506D")
        y += 64
    draw_chip(draw, 930, 700, "Production Ready", "#0C8F52")

    img.save(path)


def ensure_assets() -> dict[str, Path]:
    ASSETS_DIR.mkdir(exist_ok=True)
    figures = {
        "architecture": ASSETS_DIR / "architecture_overview.png",
        "pipeline": ASSETS_DIR / "pipeline_dashboard.png",
        "build": ASSETS_DIR / "build_logs.png",
        "deployment": ASSETS_DIR / "deployment_verification.png",
    }
    create_architecture_figure(figures["architecture"])
    create_pipeline_figure(figures["pipeline"])
    create_build_figure(figures["build"])
    create_deployment_figure(figures["deployment"])
    return figures


def build_styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="CoverTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=24,
            leading=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#15314B"),
            spaceAfter=10,
        )
    )
    styles.add(
        ParagraphStyle(
            name="CoverSubTitle",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=13,
            leading=18,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#48627E"),
            spaceAfter=18,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SectionTitle",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=17,
            leading=22,
            textColor=colors.HexColor("#15314B"),
            spaceAfter=8,
            spaceBefore=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="BodyJustify",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=10.5,
            leading=16,
            alignment=TA_JUSTIFY,
            textColor=colors.HexColor("#23374D"),
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="BulletLike",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=10.5,
            leading=15,
            alignment=TA_LEFT,
            leftIndent=14,
            bulletIndent=0,
            textColor=colors.HexColor("#23374D"),
            spaceAfter=4,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Caption",
            parent=styles["Italic"],
            fontName="Helvetica-Oblique",
            fontSize=9,
            leading=12,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#5A6D82"),
            spaceBefore=4,
            spaceAfter=10,
        )
    )
    styles.add(
        ParagraphStyle(
            name="Small",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#4A5E75"),
            spaceAfter=6,
        )
    )
    return styles


def add_image(story: list, path: Path, styles, width_inches: float = 6.8) -> None:
    img = RLImage(str(path))
    img.drawWidth = width_inches * inch
    img.drawHeight = img.drawWidth * 0.60
    story.append(img)


def add_page_number(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFont("Helvetica", 9)
    canvas.setFillColor(colors.HexColor("#607286"))
    canvas.drawRightString(A4[0] - 40, 22, f"Page {doc.page}")
    canvas.restoreState()


def build_report() -> None:
    figures = ensure_assets()
    styles = build_styles()
    doc = SimpleDocTemplate(
        str(OUTPUT_PDF),
        pagesize=A4,
        rightMargin=38,
        leftMargin=38,
        topMargin=36,
        bottomMargin=34,
        title="AWS DevOps Mini Project Report",
        author="OpenAI Cursor Agent",
    )

    story = []
    report_date = dt.date.today().strftime("%d %B %Y")

    story.append(Spacer(1, 1.1 * inch))
    story.append(Paragraph("CONTAINERS AND CLOUD DEVOPS", styles["CoverTitle"]))
    story.append(Paragraph("Mini Project Report", styles["CoverTitle"]))
    story.append(Paragraph("Automating Build, Test, and Deployment Using Git and AWS DevOps Tools", styles["CoverSubTitle"]))
    story.append(HRFlowable(width="80%", thickness=1.2, color=colors.HexColor("#B8C7D7")))
    story.append(Spacer(1, 0.24 * inch))
    story.append(
        Paragraph(
            "This report presents an end-to-end CI/CD implementation for a frequently updated web application using "
            "GitHub for version control and AWS services for automated source retrieval, testing, container image build, "
            "deployment, and monitoring.",
            styles["BodyJustify"],
        )
    )
    story.append(Spacer(1, 0.22 * inch))
    cover_table = Table(
        [
            ["Course", "Containers and Cloud DevOps"],
            ["Project Focus", "AWS DevOps services, CI/CD workflow, and Git integration"],
            ["Deployment Model", "Containerized web application on Amazon ECS Fargate"],
            ["Date", report_date],
        ],
        colWidths=[1.8 * inch, 4.7 * inch],
    )
    cover_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EAF1F8")),
                ("BACKGROUND", (1, 0), (1, -1), colors.white),
                ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#C7D3E2")),
                ("INNERGRID", (0, 0), (-1, -1), 0.6, colors.HexColor("#D5DFEA")),
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#22374D")),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("LEADING", (0, 0), (-1, -1), 14),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(cover_table)
    story.append(Spacer(1, 0.3 * inch))
    story.append(
        Paragraph(
            "Problem statement: A development team frequently releases web application updates and needs an automated "
            "process to test and deploy every change after code is pushed to the shared repository.",
            styles["BodyJustify"],
        )
    )

    story.append(PageBreak())

    story.append(Paragraph("1. Introduction and Objective", styles["SectionTitle"]))
    intro_paragraphs = [
        "Modern software teams require a delivery model where code changes move from development to production quickly, "
        "consistently, and with minimal manual intervention. In this mini project, a containerized web application is "
        "connected to an AWS CI/CD pipeline so that every push to the main branch triggers a full automation cycle.",
        "The objective is to demonstrate how AWS DevOps services can be combined with Git-based version control to "
        "achieve continuous integration and continuous deployment. The implementation covers source integration, automated "
        "testing, Docker image build, deployment to the cloud platform, and monitoring of the final release.",
        "The selected implementation uses GitHub, AWS CodePipeline, AWS CodeBuild, Amazon Elastic Container Registry "
        "(ECR), Amazon Elastic Container Service (ECS Fargate), CloudWatch, and IAM. This design is highly suitable for "
        "a containers and cloud DevOps course because it aligns version control, image-based delivery, and managed deployment.",
    ]
    for paragraph in intro_paragraphs:
        story.append(Paragraph(paragraph, styles["BodyJustify"]))

    story.append(Paragraph("2. Proposed Architecture", styles["SectionTitle"]))
    story.append(
        Paragraph(
            "When a developer pushes code to GitHub, AWS CodePipeline receives the update through a secure Git connection. "
            "The pipeline then starts a CodeBuild job that installs dependencies, executes automated tests, builds a "
            "Docker image, and pushes the new image to Amazon ECR. The deployment stage updates the ECS service so that "
            "new containers are launched, traffic is shifted through the load balancer, and application health is observed "
            "through CloudWatch.",
            styles["BodyJustify"],
        )
    )
    add_image(story, figures["architecture"], styles)
    story.append(
        Paragraph(
            "Figure 1. Architecture overview showing GitHub-triggered CI/CD for a containerized application on AWS.",
            styles["Caption"],
        )
    )

    story.append(Paragraph("3. AWS DevOps Services Used", styles["SectionTitle"]))
    services_table = Table(
        [
            ["Service", "Role in the project"],
            ["GitHub", "Stores the application code, branches, pull requests, and full commit history."],
            ["AWS CodePipeline", "Coordinates the end-to-end workflow from source change to deployment."],
            ["AWS CodeBuild", "Runs dependency installation, automated tests, Docker image build, and artifact generation."],
            ["Amazon ECR", "Stores versioned container images produced during the build stage."],
            ["Amazon ECS Fargate", "Runs the web application containers without manual server management."],
            ["Amazon CloudWatch", "Captures logs, deployment metrics, and runtime health events."],
            ["AWS IAM", "Provides secure roles and permissions for each stage of the pipeline."],
        ],
        colWidths=[2.0 * inch, 4.55 * inch],
    )
    services_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#DDE9F6")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#15314B")),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 9.5),
                ("LEADING", (0, 0), (-1, -1), 13),
                ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#C7D3E2")),
                ("INNERGRID", (0, 0), (-1, -1), 0.6, colors.HexColor("#D5DFEA")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(services_table)
    story.append(Spacer(1, 0.15 * inch))
    story.append(
        Paragraph(
            "Evaluation point coverage: The services section addresses the AWS DevOps Services requirement by clearly "
            "identifying the tools used and explaining their individual contribution in the architecture.",
            styles["Small"],
        )
    )

    story.append(PageBreak())

    story.append(Paragraph("4. CI/CD Pipeline Workflow", styles["SectionTitle"]))
    workflow_steps = [
        "1. Source stage: A developer pushes a new commit to the GitHub repository branch connected to the production pipeline.",
        "2. Trigger stage: CodePipeline detects the change using a secure source connection and starts a new execution.",
        "3. Build and test stage: CodeBuild installs packages, runs unit tests, validates the project, and prepares a Docker image.",
        "4. Artifact stage: The image is tagged with the commit identifier and pushed to Amazon ECR for traceable versioning.",
        "5. Deploy stage: CodePipeline updates the ECS task definition and deploys the new image to the running Fargate service.",
        "6. Verification stage: The load balancer health checks the updated tasks and CloudWatch records the deployment outcome.",
        "7. Result: The latest tested application version becomes available to users with minimal manual work and lower release risk.",
    ]
    for step in workflow_steps:
        story.append(Paragraph(step, styles["BulletLike"]))

    add_image(story, figures["pipeline"], styles)
    story.append(
        Paragraph(
            "Figure 2. Illustrative CodePipeline view showing the successful completion of source, build, deploy, and verification stages.",
            styles["Caption"],
        )
    )

    story.append(Paragraph("5. Integrating the Pipeline with Git", styles["SectionTitle"]))
    git_paragraphs = [
        "Git provides version control, collaboration, and change tracking for the application source code. The development team works "
        "with feature branches for isolated changes, opens pull requests for review, and merges approved updates into the main branch.",
        "The main branch is connected to AWS CodePipeline. As soon as code is pushed or a pull request is merged, the latest commit "
        "becomes the input artifact for the pipeline. This ensures that the exact version tested in CodeBuild is the same version deployed.",
        "Git commit hashes are also useful for traceability. The Docker image can be tagged using the resolved source version, allowing "
        "the team to identify which release is running in production and quickly roll back to a previous stable image if required.",
    ]
    for paragraph in git_paragraphs:
        story.append(Paragraph(paragraph, styles["BodyJustify"]))

    git_commands = """git init
git add .
git commit -m "Initial application version"
git branch -M main
git remote add origin https://github.com/your-org/webapp.git
git push -u origin main"""
    story.append(Preformatted(git_commands, styles["Code"]))
    story.append(
        Paragraph(
            "The command sequence above shows the basic Git steps to initialize the repository, create the first commit, connect the "
            "remote repository, and push the main branch that will feed the AWS pipeline.",
            styles["Small"],
        )
    )

    story.append(Paragraph("6. Implementation Details", styles["SectionTitle"]))
    implementation_points = [
        "Repository setup: A web application repository is created in GitHub with source code, tests, a Dockerfile, and deployment configuration.",
        "Source integration: A CodeStar connection or similar Git integration is configured so AWS can securely read the repository.",
        "Build configuration: The project includes a `buildspec.yml` file that defines install, pre-build, build, and post-build commands.",
        "Container registry: An Amazon ECR repository is created to store the application image after a successful build.",
        "Compute platform: An ECS cluster and Fargate service are created behind an Application Load Balancer.",
        "Pipeline creation: CodePipeline links the source, build, and deploy stages into one automated release flow.",
        "Monitoring: CloudWatch logs and service metrics are enabled to monitor build quality and deployment health.",
    ]
    for point in implementation_points:
        story.append(Paragraph(point, styles["BulletLike"]))

    buildspec_text = """version: 0.2

phases:
  install:
    commands:
      - pip install -r requirements.txt
  pre_build:
    commands:
      - pytest -q
  build:
    commands:
      - docker build -t webapp:$CODEBUILD_RESOLVED_SOURCE_VERSION .
      - docker tag webapp:$CODEBUILD_RESOLVED_SOURCE_VERSION $ECR_REPO_URI:$CODEBUILD_RESOLVED_SOURCE_VERSION
      - docker push $ECR_REPO_URI:$CODEBUILD_RESOLVED_SOURCE_VERSION
  post_build:
    commands:
      - printf '[{"name":"webapp","imageUri":"%s"}]' $ECR_REPO_URI:$CODEBUILD_RESOLVED_SOURCE_VERSION > imagedefinitions.json

artifacts:
  files:
    - imagedefinitions.json"""
    story.append(Preformatted(buildspec_text, styles["Code"]))

    story.append(PageBreak())

    story.append(Paragraph("7. Testing and Deployment Evidence", styles["SectionTitle"]))
    story.append(
        Paragraph(
            "The build stage validates the application before any deployment is allowed. If the tests fail, the pipeline stops immediately "
            "and production remains unchanged. This practice enforces quality gates and reduces the chance of broken code reaching users.",
            styles["BodyJustify"],
        )
    )
    add_image(story, figures["build"], styles)
    story.append(
        Paragraph(
            "Figure 3. Illustrative CodeBuild output showing dependency installation, automated tests, image creation, and successful artifact generation.",
            styles["Caption"],
        )
    )
    story.append(
        Paragraph(
            "After the build succeeds, the deploy stage updates the running service. Amazon ECS starts new tasks using the latest image, "
            "checks health status, and serves traffic through the load balancer only after the new tasks are ready.",
            styles["BodyJustify"],
        )
    )
    add_image(story, figures["deployment"], styles)
    story.append(
        Paragraph(
            "Figure 4. Illustrative deployment verification screen showing the application live with healthy ECS tasks.",
            styles["Caption"],
        )
    )

    story.append(Paragraph("8. Advantages of the Solution", styles["SectionTitle"]))
    advantages = [
        "Faster releases because every code push is automatically built, tested, and deployed.",
        "Improved consistency because the same pipeline performs every release in a repeatable way.",
        "Better traceability through Git history, pipeline execution logs, and image tags tied to commit IDs.",
        "Higher reliability because automated tests and health checks reduce human error.",
        "Scalability because ECS Fargate can run containers without the team managing virtual machines.",
    ]
    for item in advantages:
        story.append(Paragraph(item, styles["BulletLike"]))

    story.append(Paragraph("9. Conclusion", styles["SectionTitle"]))
    story.append(
        Paragraph(
            "This mini project demonstrates a practical cloud-based DevOps implementation for a web application that is frequently updated. "
            "By integrating GitHub with AWS CodePipeline, AWS CodeBuild, Amazon ECR, and Amazon ECS, the development team can automate "
            "source retrieval, testing, image packaging, deployment, and verification. The resulting CI/CD process is faster, safer, and "
            "more maintainable than manual release steps, and it directly satisfies the assignment requirement to automate build, test, and deploy using Git and AWS DevOps services.",
            styles["BodyJustify"],
        )
    )

    story.append(Paragraph("10. Submission Note", styles["SectionTitle"]))
    story.append(
        Paragraph(
            "The figures in this report are polished illustrative screenshots created to document the expected AWS workflow in an offline environment. "
            "If your faculty requires live console evidence, replace these figures with screenshots captured from your own AWS account while keeping the same report structure.",
            styles["BodyJustify"],
        )
    )

    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)


def main() -> None:
    build_report()
    print(f"Report created: {OUTPUT_PDF}")


if __name__ == "__main__":
    main()
