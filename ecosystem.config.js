module.exports = {
    apps: [
      {
        name: "streamlit_app",
        script: "python",
        args: "-m streamlit run Streamlit_show.py --server.port 8501",
        cwd: "C:/Users/spd-d/OneDrive/Desktop/Camera_project/version_5",
        autorestart: true,
        watch: false,
      },
      {
        name: "camera_project",
        script: "python",
        args: "main_1.py",
        cwd: "C:/Users/spd-d/OneDrive/Desktop/Camera_project/version_5",
        autorestart: true,
        watch: true,
      },
    ],
  };
  