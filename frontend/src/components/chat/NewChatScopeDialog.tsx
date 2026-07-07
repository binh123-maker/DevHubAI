import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { workspaceApi, Workspace } from '@/api/workspace.api';
import { folderApi, Folder } from '@/api/folder.api';
import { documentApi, Document } from '@/api/document.api';

export interface ScopeSelection {
  chatName: string;
  chatMode: 'global' | 'workspace' | 'folder' | 'document' | 'website';
  workspaceId?: string;
  folderId?: string;
  documentId?: string;
}

interface NewChatScopeDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onStartChat: (selection: ScopeSelection) => void;
}

export function NewChatScopeDialog({ open, onOpenChange, onStartChat }: NewChatScopeDialogProps) {
  const [chatName, setChatName] = useState('');
  const [chatMode, setChatMode] = useState<'global' | 'workspace' | 'folder' | 'document' | 'website'>('global');
  
  const [workspaces, setWorkspaces] = useState<Workspace[]>([]);
  const [folders, setFolders] = useState<Folder[]>([]);
  const [documents, setDocuments] = useState<Document[]>([]);
  
  const [workspaceId, setWorkspaceId] = useState<string>('');
  const [folderId, setFolderId] = useState<string>('');
  const [documentId, setDocumentId] = useState<string>('');

  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (open) {
      // Reset state
      setChatName('');
      setChatMode('global');
      setWorkspaceId('');
      setFolderId('');
      setDocumentId('');
      
      // Load workspaces
      workspaceApi.list().then(res => setWorkspaces(res.data)).catch(console.error);
    }
  }, [open]);

  useEffect(() => {
    if (workspaceId && (chatMode === 'folder' || chatMode === 'document')) {
      folderApi.list(workspaceId).then(res => setFolders(res.data)).catch(console.error);
    } else {
      setFolders([]);
      setFolderId('');
    }
  }, [workspaceId, chatMode]);

  useEffect(() => {
    if (workspaceId && folderId && chatMode === 'document') {
      documentApi.list(workspaceId, folderId).then(res => setDocuments(res.data)).catch(console.error);
    } else {
      setDocuments([]);
      setDocumentId('');
    }
  }, [workspaceId, folderId, chatMode]);

  const handleStart = () => {
    onStartChat({
      chatName: chatName.trim(),
      chatMode,
      workspaceId: workspaceId || undefined,
      folderId: folderId || undefined,
      documentId: documentId || undefined,
    });
    onOpenChange(false);
  };

  const isFormValid = () => {
    if (chatMode === 'workspace' && !workspaceId) return false;
    if (chatMode === 'folder' && (!workspaceId || !folderId)) return false;
    if (chatMode === 'document' && (!workspaceId || !folderId || !documentId)) return false;
    return true;
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Bắt đầu cuộc trò chuyện mới</DialogTitle>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="grid gap-2">
            <Label htmlFor="chatName">Tên trò chuyện (tùy chọn)</Label>
            <Input
              id="chatName"
              placeholder="Tự động tạo nếu để trống..."
              value={chatName}
              onChange={(e) => setChatName(e.target.value)}
            />
          </div>
          
          <div className="grid gap-2">
            <Label>Phạm vi kiến thức</Label>
            <Select value={chatMode} onValueChange={(v: any) => setChatMode(v)}>
              <SelectTrigger>
                <SelectValue placeholder="Chọn phạm vi" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="global">🌐 Entire Knowledge Base</SelectItem>
                <SelectItem value="workspace">📁 Workspace</SelectItem>
                <SelectItem value="folder">📂 Folder</SelectItem>
                <SelectItem value="document">📄 Document</SelectItem>
                <SelectItem value="website">🌐 Imported Websites</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {(chatMode === 'workspace' || chatMode === 'folder' || chatMode === 'document') && (
            <div className="grid gap-2 animate-in fade-in slide-in-from-top-2">
              <Label>Workspace</Label>
              <Select value={workspaceId} onValueChange={setWorkspaceId}>
                <SelectTrigger>
                  <SelectValue placeholder="Chọn Workspace" />
                </SelectTrigger>
                <SelectContent>
                  {workspaces.map(w => (
                    <SelectItem key={w.id} value={w.id}>{w.name}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          )}

          {(chatMode === 'folder' || chatMode === 'document') && workspaceId && (
            <div className="grid gap-2 animate-in fade-in slide-in-from-top-2">
              <Label>Folder</Label>
              <Select value={folderId} onValueChange={setFolderId}>
                <SelectTrigger>
                  <SelectValue placeholder="Chọn Folder" />
                </SelectTrigger>
                <SelectContent>
                  {folders.map(f => (
                    <SelectItem key={f.id} value={f.id}>{f.name}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          )}

          {chatMode === 'document' && workspaceId && folderId && (
            <div className="grid gap-2 animate-in fade-in slide-in-from-top-2">
              <Label>Document</Label>
              <Select value={documentId} onValueChange={setDocumentId}>
                <SelectTrigger>
                  <SelectValue placeholder="Chọn Document" />
                </SelectTrigger>
                <SelectContent>
                  {documents.map(d => (
                    <SelectItem key={d.id} value={d.id}>{d.title}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          )}
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>Hủy</Button>
          <Button onClick={handleStart} disabled={!isFormValid()}>Bắt đầu</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
