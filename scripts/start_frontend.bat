@echo off
title Start Frontend Service
cd /d "%~dp0.."
cd web
npm run dev
