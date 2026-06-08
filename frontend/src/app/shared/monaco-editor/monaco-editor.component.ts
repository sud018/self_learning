import {
  AfterViewInit, Component, ElementRef,
  Input, OnChanges, OnDestroy, Output, EventEmitter, SimpleChanges, ViewChild
} from '@angular/core';
import { MonacoLoaderService } from '../../core/monaco-loader.service';

@Component({
  selector: 'app-monaco-editor',
  standalone: true,
  template: `<div #host class="monaco-inner"></div>`,
  styles: [`:host { display:block; height:100%; } .monaco-inner { height:100%; min-height:300px; }`]
})
export class MonacoEditorComponent implements AfterViewInit, OnChanges, OnDestroy {
  @ViewChild('host') host!: ElementRef<HTMLDivElement>;
  @Input() value = '';
  @Input() language = 'java';
  @Output() valueChange = new EventEmitter<string>();

  private editor: any = null;

  constructor(private loader: MonacoLoaderService) {}

  ngAfterViewInit() {
    this.loader.load().then(() => {
      const monaco = (window as any).monaco;
      this.editor = monaco.editor.create(this.host.nativeElement, {
        value: this.value ?? '',
        language: this.language,
        theme: 'vs-dark',
        automaticLayout: true,
        minimap: { enabled: false },
        fontSize: 14,
        lineNumbers: 'on',
        scrollBeyondLastLine: false,
        fontFamily: '"Fira Code", "Cascadia Code", Consolas, "Courier New", monospace',
        renderLineHighlight: 'all',
        padding: { top: 14, bottom: 14 },
        tabSize: 2,
        insertSpaces: true,
        cursorStyle: 'line',
        cursorBlinking: 'smooth',
        wordWrap: 'off',
        suggest: { showKeywords: true },
        quickSuggestions: true,
      });
      this.editor.onDidChangeModelContent(() => {
        this.valueChange.emit(this.editor.getValue());
      });
    });
  }

  ngOnChanges(changes: SimpleChanges) {
    if (!this.editor) return;
    if (changes['value']) {
      const v = changes['value'].currentValue ?? '';
      if (this.editor.getValue() !== v) this.editor.setValue(v);
    }
    if (changes['language'] && !changes['language'].firstChange) {
      const monaco = (window as any).monaco;
      if (monaco) monaco.editor.setModelLanguage(this.editor.getModel(), changes['language'].currentValue);
    }
  }

  ngOnDestroy() { this.editor?.dispose(); }
}
